# embeddings/rag.py
import os
import sys

# --- PATH & MODULE RESOLUTION FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)   # Points to 'ai-pipeline'
project_root = os.path.dirname(parent_dir)  # Points to workspace root

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict

from embeddings.search import search
from embeddings.router import classify_question, answer_general
from embeddings.memory import extract_name

# Handle fallback options to find environment context safely
if os.path.exists(os.path.join(project_root, ".env")):
    load_dotenv(os.path.join(project_root, ".env"))
else:
    load_dotenv(os.path.join(parent_dir, ".env"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MIN_SIMILARITY = 0.45

# --------------------------------------------------
# LANGUAGE DETECTION + TRANSLATION
# --------------------------------------------------

def detect_language_and_translate(text: str) -> dict:
    """Detect language and translate to English."""
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


def translate_answer_to_language(answer: str, language_name: str) -> str:
    """Translate fallback or short system tracking messages accurately."""
    if language_name.lower() == "english":
        return answer

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Translate the following health information into {language_name}.\n"
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

def ask(question: str, history: List[Dict] = []) -> dict:
    # STEP 1: Detect language
    detection = detect_language_and_translate(question)
    language_code = detection["language_code"]
    language_name = detection["language_name"]
    english_question = detection["english"]

    print(f"[Original]   {question}")
    print(f"[Language]   {language_name}")
    print(f"[English]    {english_question}")

    # STEP 2: ROUTE QUESTION FIRST
    question_type = classify_question(english_question)
    
    if question_type == "memory":
        name = extract_name(history)
        final_answer = f"You previously told me your name is {name}." if name else "I do not know your name yet."

        if language_name.lower() != "english":
            final_answer = translate_answer_to_language(final_answer, language_name)

        return {
            "answer": final_answer,
            "sources": [],
            "score": 1.0,
            "question_type": "memory",
            "detected_language": language_code,
            "language_name": language_name
        }

    print(f"[Route] {question_type}")

    # GENERAL QUESTIONS ROUTING
    if question_type == "general":
        answer = answer_general(question, language_name, history)
        return {
            "answer": answer,
            "sources": [],
            "score": 0.0,
            "question_type": "general",
            "detected_language": language_code,
            "language_name": language_name
        }

    # HEALTH QUESTIONS → PGVECTOR
    results = search(english_question, top_k=5)
    relevant = [r for r in results if r["similarity"] >= MIN_SIMILARITY]

    if not relevant:
        fallback = (
            "I could not find relevant health information in the HealthBridge knowledge base. "
            "Please consult a qualified healthcare provider."
        )
        return {
            "answer": translate_answer_to_language(fallback, language_name),
            "sources": [],
            "score": 0.0,
            "question_type": "health",
            "detected_language": language_code,
            "language_name": language_name
        }

    # BUILD CONTEXT
    context_parts = [f"[Source: {r['source']}]\n{r['content']}" for r in relevant]
    context = "\n\n---\n\n".join(context_parts)[:6000]

    # COMPASSIONATE SYSTEM PROMPT
    messages = [
        {
            "role": "system",
            "content": (
                f"You are HealthBridge Africa's health assistant.\n"
                f"The user speaks {language_name}.\n"
                f"You MUST answer entirely in {language_name}.\n\n"
                "RULES:\n"
                "1. Use ONLY the provided context.\n"
                "2. Never diagnose diseases.\n"
                "3. Never prescribe medication.\n"
                "4. If information is missing, say so.\n"
                "5. Recommend professional care when needed.\n\n"
                "FORMATTING RULES:\n"
                "- Start with a direct answer\n"
                "- Use short paragraphs\n"
                "- Use bullet points when appropriate (Max 4)\n"
                "- End with medical advice if necessary.\n"
                "- Use emojis to make it more engaging.\n\n"
                "- CRITICAL: If you cannot find a clear response or detect repetitive generation loops, output: "
                "'I am having difficulty generating a reliable answer. Please try rephrasing your question.'\n"
                "- CRITICAL: NEVER write in English if the user's question is in an African dialect.\n\n"
                f"CONTEXT:\n{context}"
            )
        }
    ]

    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({
        "role": "user",
        "content": f"Original Question: {question}\nEnglish Meaning: {english_question}"
    })

    # GENERATE INFERENCE RESPONSE
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.3
    )

    final_answer = response.choices[0].message.content.strip()

    # HALLUCINATION LOOP DETECTION
    words = final_answer.split()
    if len(words) > 20:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.30:
            print("⚠ Hallucination loop detected")
            loop_fallback = "I am having difficulty generating a reliable answer. Please try rephrasing your question."
            return {
                "answer": translate_answer_to_language(loop_fallback, language_name),
                "sources": [r["source"] for r in relevant],
                "score": relevant[0]["similarity"] if relevant else 0.0,
                "question_type": "health",
                "detected_language": language_code,
                "language_name": language_name
            }

    return {
        "answer": final_answer,
        "sources": [r["source"] for r in relevant],
        "score": relevant[0]["similarity"] if relevant else 0.0,
        "question_type": "health",
        "detected_language": language_code,
        "language_name": language_name
    }