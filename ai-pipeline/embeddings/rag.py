# embeddings/rag.py

from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict
import os

from embeddings.search import search
from embeddings.router import classify_question, answer_general
from embeddings.memory import extract_name

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MIN_SIMILARITY = 0.45


# --------------------------------------------------
# LANGUAGE DETECTION + TRANSLATION
# --------------------------------------------------

def detect_language_and_translate(text: str) -> dict:
    """
    Detect language and translate to English.

    Returns:
    {
        "language_code": "am",
        "language_name": "Amharic",
        "english": "What is malaria?"
    }
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
You are a medical language detector and translator.

TASK:
1. Detect the language.
2. Translate to English.

IMPORTANT MEDICAL TERMS:

AMHARIC
--------
ወባ = malaria
ኮሌራ = cholera
ነቀርሳ = tuberculosis
የራስ ህመም = headache
ትኩሳት = fever
ተቅማጥ = diarrhea

AFAAN OROMO
-----------
busaa = malaria
koleeraa = cholera
dhukkuba sombaa = tuberculosis
mataa na dhukkuba = headache
hoo'a qaamaa = fever
garaa kaasaa = diarrhea
qaamni koo ni dadhaba = fatigue
ija koo ni dhukkuba = eye pain

SWAHILI
--------
malaria = malaria
kipindupindu = cholera
kifua kikuu = tuberculosis
maumivu ya kichwa = headache
homa = fever
kuhara = diarrhea

PIDGIN
-------
malaria = malaria
cholera = cholera
tuberculosis = tuberculosis
head dey pain me = headache
body dey hot = fever
running stomach = diarrhea

TWI
----
atiridii = malaria
tirim = headache
yam yareɛ = sickness

Language Codes:
am = Amharic
om = Afaan Oromo
sw = Swahili
ha = Hausa
pcm = Nigerian Pidgin
tw = Twi
fr = French
en = English

Respond EXACTLY:

LANGUAGE_CODE: code
LANGUAGE_NAME: name
ENGLISH: translation
"""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0,
        max_tokens=150
    )

    content = response.choices[0].message.content.strip()

    result = {
        "language_code": "en",
        "language_name": "English",
        "english": text
    }

    for line in content.split("\n"):
        if line.startswith("LANGUAGE_CODE:"):
            result["language_code"] = line.split(":", 1)[1].strip().lower()

        elif line.startswith("LANGUAGE_NAME:"):
            result["language_name"] = line.split(":", 1)[1].strip()

        elif line.startswith("ENGLISH:"):
            result["english"] = line.split(":", 1)[1].strip()

    return result


# --------------------------------------------------
# TRANSLATE FALLBACK MESSAGES
# --------------------------------------------------

def translate_answer_to_language(
    answer: str,
    language_name: str
) -> str:

    if language_name.lower() == "english":
        return answer

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Translate the following health information into "
                    f"{language_name}.\n"
                    "Keep medical meaning accurate.\n"
                    "Return ONLY the translation."
                )
            },
            {
                "role": "user",
                "content": answer
            }
        ],
        temperature=0,
        max_tokens=600
    )

    return response.choices[0].message.content.strip()


# --------------------------------------------------
# MAIN RAG FUNCTION
# --------------------------------------------------

def ask(
    question: str,
    history: List[Dict] = []
) -> dict:

    # ------------------------------------------
    # STEP 1: Detect language
    # ------------------------------------------

    detection = detect_language_and_translate(question)

    language_code = detection["language_code"]
    language_name = detection["language_name"]
    english_question = detection["english"]

    print(f"[Original]   {question}")
    print(f"[Language]   {language_name}")
    print(f"[English]    {english_question}")

    # ------------------------------------------
    # STEP 2: ROUTE QUESTION FIRST
    # ------------------------------------------

    question_type = classify_question(
        english_question
    )
    
    if question_type == "memory":

        name = extract_name(history)

        if name:

            final_answer = (
                f"You previously told me your name is {name}."
            )

        else:

            final_answer = (
                "I do not know your name yet."
            )

        if language_name != "English":

            final_answer = translate_answer_to_language(
                final_answer,
                language_name
            )

        return {
            "answer": final_answer,
            "sources": [],
            "score": 1.0,
            "question_type": "memory",
            "detected_language": language_code,
            "language_name": language_name
        }

    print(f"[Route] {question_type}")

    # ------------------------------------------
    # GENERAL QUESTIONS
    # ------------------------------------------

    if question_type == "general":

        answer = answer_general(
            question,
            language_name,
            history
        )

        return {
            "answer": answer,
            "sources": [],
            "score": 0.0,
            "question_type": "general",
            "detected_language": language_code,
            "language_name": language_name
        }

    # ------------------------------------------
    # HEALTH QUESTIONS → PGVECTOR
    # ------------------------------------------

    results = search(
        english_question,
        top_k=5
    )

    relevant = [
        r for r in results
        if r["similarity"] >= MIN_SIMILARITY
    ]

    if not relevant:

        fallback = (
            "I could not find relevant health information "
            "in the HealthBridge knowledge base. "
            "Please consult a qualified healthcare provider."
        )

        return {
            "answer": translate_answer_to_language(
                fallback,
                language_name
            ),
            "sources": [],
            "score": 0.0,
            "question_type": "health",
            "detected_language": language_code,
            "language_name": language_name
        }

    # ------------------------------------------
    # BUILD CONTEXT
    # ------------------------------------------

    context_parts = []

    for r in relevant:

        context_parts.append(
            f"[Source: {r['source']}]\n"
            f"{r['content']}"
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    context = context[:6000]

    # ------------------------------------------
    # PROMPT
    # ------------------------------------------

    messages = [
        {
            "role": "system",
            "content": (
                f"You are HealthBridge Africa's health assistant.\n"
                f"The user speaks {language_name}.\n\n"

                f"You MUST answer entirely in "
                f"{language_name}.\n\n"

                "RULES:\n"
                "1. Use ONLY the provided context.\n"
                "2. Never diagnose diseases.\n"
                "3. Never prescribe medication.\n"
                "4. If information is missing, say so.\n"
                "5. Recommend professional care when needed.\n"

                "\nFORMATTING RULES:\n"
                "- Start with a direct answer\n"
                "- Use short paragraphs\n"
                "- Use bullet points when appropriate\n"
                "- Maximum 4 bullet points\n"
                "- Avoid long walls of text\n"
                "- End with medical advice if necessary.\n"
                "- Use emojis to make it more engaging.\n\n"
                "- CRITICAL: If the user asks a health question but you don't have a good answer, do NOT try to make something up. Instead, say: 'I am having difficulty generating a reliable answer. Please try rephrasing your question.'\n"
                "- CRITICAL: If you detect that you are repeating yourself in a loop, stop and say: 'I am having difficulty generating a reliable answer. Please try rephrasing your question.'\n\n"
                "- CRITICAL: Always keep the language consistent with the user's question. If you are not sure, use the language of the last message from the user.\n\n"
                "- CRITICAL: NEVER write in English if the user's question is not in English. Always respond in the user's language."
                "- CRITICAL: If you are not sure about the user's language, default to the language of the last user message. Do NOT write in English if the user's question is not in English.\n\n"
                "- be perfect at detecting and responding in the user's language. If you are not sure, use the language of the last user message. Do NOT write in English if the user's question is not in English.\n\n"

                f"\nCONTEXT:\n{context}"
            )
        }
    ]

    # history

    for msg in history[-6:]:

        messages.append(
            {
                "role": msg["role"],
                "content": msg["content"]
            }
        )

    messages.append(
        {
            "role": "user",
            "content": (
                f"Original Question: {question}\n"
                f"English Meaning: {english_question}"
            )
        }
    )

    # ------------------------------------------
    # GENERATE ANSWER
    # ------------------------------------------

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.3
    )

    final_answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    # ------------------------------------------
    # HALLUCINATION LOOP DETECTION
    # ------------------------------------------

    words = final_answer.split()

    if len(words) > 20:

        unique_ratio = (
            len(set(words))
            / len(words)
        )

        if unique_ratio < 0.30:

            print(
                "⚠ Hallucination loop detected"
            )

            final_answer = (
                translate_answer_to_language(
                    (
                        "I am having difficulty "
                        "generating a reliable answer. "
                        "Please try rephrasing your question."
                    ),
                    language_name
                )
            )

    # ------------------------------------------
    # RETURN
    # ------------------------------------------

    return {
        "answer": final_answer,
        "sources": [
            r["source"]
            for r in relevant
        ],
        "score": relevant[0]["similarity"],
        "question_type": "health",
        "detected_language": language_code,
        "language_name": language_name
    }











# # embeddings/rag.py
# from groq import Groq
# from dotenv import load_dotenv
# from typing import List, Dict
# import os
# from embeddings.search import search

# load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# MIN_SIMILARITY = 0.45   # ← lowered from 0.45
# from embeddings.router import classify_question, answer_general


# def detect_language_and_translate(text: str) -> dict:
#     """
#     Use Groq Llama to BOTH detect language AND translate in one call.
#     Much more accurate than langdetect for African languages.
#     Returns: {"language_code": "am", "language_name": "Amharic", "english": "..."}
#     """
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",   # ← stronger model
#         messages=[
#             {
#                 "role": "system",
#                 "content": """
# You are a medical language detector and translator for African languages.

# Given a health question, you must:
# 1. Detect what language it is written in
# 2. Translate it to English

# CRITICAL MEDICAL TERMS — never mistranslate these:
# - ወባ (Amharic) = malaria (NOT rabies)
# - busaa (Oromo) = malaria
# - ኮሌራ (Amharic) = cholera
# - ነቀርሳ (Amharic) = tuberculosis
# - dhukkuba sombaa (Oromo) = tuberculosis
# - koleeraa (Oromo) = cholera
# - gad-dhabbuu (Oromo) = malnutrition
# - dhukkuba ijaa (Oromo) = trachoma (eye disease)

# LANGUAGE CODES:
# - Amharic → am
# - Afaan Oromoo → om
# - Swahili → sw
# - Twi → tw
# - Nigerian Pidgin → pcm
# - Hausa → ha
# - English → en
# - French → fr

# Respond in this EXACT format, nothing else:
# LANGUAGE_CODE: [code]
# LANGUAGE_NAME: [name]
# ENGLISH: [english translation]
# """
#             },
#             {"role": "user", "content": text}
#         ],
#         temperature=0.0,
#         max_tokens=150
#     )

#     content = response.choices[0].message.content.strip()
#     print(f"[LLM Detection Output]: {content}")

#     # Parse the response
#     lines = content.split("\n")
#     result = {
#         "language_code": "en",
#         "language_name": "English",
#         "english":       text   # fallback to original
#     }

#     for line in lines:
#         if line.startswith("LANGUAGE_CODE:"):
#             result["language_code"] = line.split(":", 1)[1].strip().lower()
#         elif line.startswith("LANGUAGE_NAME:"):
#             result["language_name"] = line.split(":", 1)[1].strip()
#         elif line.startswith("ENGLISH:"):
#             result["english"] = line.split(":", 1)[1].strip()

#     return result


# def translate_answer_to_language(answer: str, language_name: str) -> str:
#     """Translate English answer back to user's language."""
#     if language_name.lower() == "english":
#         return answer

#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",   # ← smaller model for translation
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     f"You are a health information translator. "
#                     f"Translate the following English health text to {language_name}. "
#                     f"Keep medical terms accurate. "
#                     f"Keep the response simple and easy to understand. "
#                     f"Respond with ONLY the translated text, nothing else."
#                     "FORMATTING RULES:\n"
#                         "- Use short paragraphs (2-3 sentences max)\n"
#                         "- Use bullet points (•) for lists of symptoms or steps\n"
#                         "- Start with a direct answer to the question\n"
#                         "- End with: 'Please consult a healthcare provider for personal advice.'\n"
#                         "- Never write walls of text\n"
#                         "- Maximum 4 bullet points\n\n"
#                 )
#             },
#             {"role": "user", "content": answer}
#         ],
#         temperature=0.1,
#         max_tokens=600
#     )
#     return response.choices[0].message.content.strip()


# def ask(question: str, history: List[Dict] = []) -> dict:
#     """Full RAG pipeline with accurate language detection and memory."""
    
    
#     # Step 1: Detect language + translate to English in ONE call
#     detection = detect_language_and_translate(question)
#     language_code = detection["language_code"]
#     language_name = detection["language_name"]
#     english_question = detection["english"]
    
    

#     print(f"[Original]   {question}")
#     print(f"[Language]   {language_name} ({language_code})")
#     print(f"[Translated] {english_question}")

#     # Step 2: Search pgvector with English question
#     results = search(english_question, top_k=5)

#     # Step 3: Filter relevant chunks
#     relevant = [r for r in results if r["similarity"] >= MIN_SIMILARITY]

#     if not relevant:
#         # Return "not found" message in user's language
#         not_found_english = (
#             "I could not find relevant health information for that question "
#             "in the HealthBridge knowledge base. "
#             "Please consult a qualified healthcare provider."
#         )
#         not_found_translated = translate_answer_to_language(
#             not_found_english, language_name
#         )
#         return {
#             "answer":  not_found_translated,
#             "sources": [],
#             "score":   0.0
#         }

#     # Step 4: Build context from chunks
#     context_parts = []
#     for r in relevant:
#         context_parts.append(
#             f"[Source: {r['source']} | Condition: {r.get('condition', 'general')}]\n"
#             f"{r['content']}"
#         )
#     context = "\n\n---\n\n".join(context_parts)
#     context = context[:6000]

#     # Step 5: Build messages with history
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 f"You are HealthBridge Africa's health information assistant.\n"
#                 f"The user speaks {language_name}.\n"
#                 f"You MUST write your ENTIRE answer in {language_name}.\n"
#                 f"If {language_name} is not English, do NOT write in English.\n\n"
#                 "RULES:\n"
#                 "1. Use ONLY the context provided below.\n"
#                 "2. Never diagnose diseases.\n"
#                 "3. Never prescribe medications.\n"
#                 "4. If the answer is not in the context, say so clearly "
#                 f"in {language_name}.\n"
#                 "5. Always recommend professional medical care for serious symptoms.\n"
#                 "6. Keep responses simple and easy to understand.\n\n"
#                 f"CONTEXT:\n{context}"
#             )
#         }
#     ]

#     # Add conversation history (last 6 messages = 3 turns)
#     for msg in history[-6:]:
#         messages.append({
#             "role":    msg["role"],
#             "content": msg["content"]
#         })

#     # Add current question in original language
#     messages.append({
#         "role":    "user",
#         "content":  f"Original Question: {question}\n"
#         f"English Meaning: {english_question}"   # send original language question
#     })

#     # Step 6: Generate answer
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",   # ← stronger model
#         messages=messages,
#         max_tokens=500,
#         temperature=0.3
#     )
    
#     final_answer = response.choices[0].message.content
    
#     words = final_answer.split()
#     if len(words) > 20:
#         unique_words = len(set(words))
#         total_words = len(words)
#         repetition_ratio = 1 - (unique_words / total_words)
#         if repetition_ratio < 0.3:  # If more than 30% of the words are repeated
#             print("hullicination loop detected - returning fallback message")        
#             final_answer = translate_answer_to_language(
#                 "I am having trouble generating a good answer for that question. "
#                 "Please try rephrasing or asking about a different health topic.",
#                 language_name
#             )
            
#             return {
#                 "answer": final_answer,
#                 "sources": [r["source"] for r in relevant],
#                 "score": relevant[0]["similarity"],
#                 "detected_language": language_code,
#                 "language_name": language_name
#             }
    
#     # english_answer = response.choices[0].message.content

#     # # Step 7: Translate answer back if needed
#     # # (LLM should already answer in correct language but this is a safety net)
#     # final_answer = translate_answer_to_language(english_answer, language_name)
    
#     question_type = classify_question(english_question)
#     print(f"[Route] {question_type}")
#     if question_type == "general":
#         print("Routing to general LLM handler...")
#         final_answer = answer_general(english_question, language_name, history)

#         return {
#             "answer":          final_answer,
#             "sources":         [r["source"] for r in relevant],
#             "score":           relevant[0]["similarity"],
#             "detected_language": language_code,
#             "language_name":   language_name
#         }


# if __name__ == "__main__":
#     test_questions = [
#         "What are symptoms of malaria?",           # English
#         "የወባ በሽታ ምልክቶች ምንድን ናቸው?",              # Amharic
#         "Busaan malattoolee isaa maalidha?",        # Oromo
#         "Dalili za malaria ni zipi?",               # Swahili
#         "How do I prevent cholera?",               # English
#         "how do I repair a bicycle?",              # should say not found
#     ]

#     for q in test_questions:
#         print(f"\n{'='*55}")
#         print(f"Q: {q}")
#         result = ask(q)
#         print(f"Score:    {result['score']}")
#         print(f"Language: {result.get('language_name', '?')}")
#         print(f"Sources:  {result['sources']}")
#         print(f"Answer:   {result['answer'][:300]}")