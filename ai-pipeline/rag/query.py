# import os
# import psycopg2
# from google import genai
# from google.genai import types
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI(
#     api_key=os.environ.get("GROQ_API_KEY"),
#     base_url="https://api.groq.com/openai/v1"
# )
# gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# # --------------------------------------------------
# # LANGUAGE DETECTION + TRANSLATION
# # --------------------------------------------------

# def detect_language_and_translate(text: str) -> dict:
#     """Detect language and translate to English."""
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         # model ="gemini-2.5-flash",
#         messages=[
#             {
#                 "role": "system",
#                 "content": """
# You are a medical language detector and translator.

# TASK:
# 1. Detect the language.
# 2. Translate to English.

# IMPORTANT MEDICAL TERMS:

# AMHARIC
# --------
# ወባ = malaria
# ኮሌራ = cholera
# ነቀርሳ = tuberculosis
# የራስ ህመም = headache
# ትኩሳት = fever
# ተቅማጥ = diarrhea

# AFAAN OROMO
# -----------
# busaa = malaria
# koleeraa = cholera
# dhukkuba sombaa = tuberculosis
# mataa na dhukkuba = headache
# hoo'a qaamaa = fever
# garaa kaasaa = diarrhea
# qaamni koo ni dadhaba = fatigue
# ija koo ni dhukkuba = eye pain

# SWAHILI
# --------
# malaria = malaria
# kipindupindu = cholera
# kifua kikuu = tuberculosis
# maumivu ya kichwa = headache
# homa = fever
# kuhara = diarrhea

# PIDGIN
# -------
# malaria = malaria
# cholera = cholera
# tuberculosis = tuberculosis
# head dey pain me = headache
# body dey hot = fever
# running stomach = diarrhea

# TWI
# ----
# atiridii = malaria
# tirim = headache
# yam yareɛ = sickness

# Language Codes:
# am = Amharic
# om = Afaan Oromo
# sw = Swahili
# ha = Hausa
# pcm = Nigerian Pidgin
# tw = Twi
# fr = French
# en = English

# Respond EXACTLY:

# LANGUAGE_CODE: code
# LANGUAGE_NAME: name
# ENGLISH: translation
# """
#             },
#             {
#                 "role": "user",
#                 "content": text
#             }
#         ],
#         temperature=0.0,
#         max_tokens=150
#     )

#     content = response.choices[0].message.content.strip()

#     result = {
#         "language_code": "en",
#         "language_name": "English",
#         "english": text
#     }

#     for line in content.split("\n"):
#         if line.startswith("LANGUAGE_CODE:"):
#             result["language_code"] = line.split(":", 1)[1].strip().lower()
#         elif line.startswith("LANGUAGE_NAME:"):
#             result["language_name"] = line.split(":", 1)[1].strip()
#         elif line.startswith("ENGLISH:"):
#             result["english"] = line.split(":", 1)[1].strip()

#     return result


# def translate_answer_to_language(answer: str, language_name: str) -> str:
#     """Translate fallback or short system tracking messages accurately."""
#     if language_name.lower() == "english":
#         return answer

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     f"Translate the following health information into {language_name}.\n"
#                     "Keep medical meaning accurate.\n"
#                     "Return ONLY the translation."
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": answer
#             }
#         ],
#         temperature=0,
#         max_tokens=600
#     )
#     return response.choices[0].message.content.strip()


# def get_query_embedding(text: str) -> list:
#     """Generate a normalized 768-dim embedding for a search query via Gemini."""
#     result = gemini_client.models.embed_content(
#         model="gemini-embedding-001",
#         contents=text,
#         config=types.EmbedContentConfig(
#             task_type="RETRIEVAL_QUERY",
#             output_dimensionality=768
#         )
#     )
#     vector = result.embeddings[0].values
#     norm = sum(v * v for v in vector) ** 0.5
#     normalized = [v / norm for v in vector] if norm > 0 else vector
#     return normalized


# def ask_rag(question: str, language: str = "English", history: list = []) -> dict:
#     """Full RAG: Embed query via Gemini, search Neon DB, then answer with Groq Llama 3."""

#     # # Step 1: Translate query to English for better semantic search
#     # search_query = question
#     # try:
#     #     trans_res = client.chat.completions.create(
#     #         model="llama-3.1-8b-instant",
#     #         messages=[
#     #             {"role": "system", "content": "Translate the following query strictly to English. Return ONLY the English text, nothing else."},
#     #             {"role": "user", "content": question}
#     #         ],
#     #         max_tokens=150,
#     #         temperature=0.0
#     #     )
#     #     search_query = trans_res.choices[0].message.content.strip() or question
#     # except Exception as e:
#     #     print(f"Translation failed: {e}")
#     # Step 1: Detect language + translate
    
#     detection = detect_language_and_translate(question)

#     language_code = detection["language_code"]
#     language_name = detection["language_name"]
#     search_query = detection["english"]

#     print(f"[Original] {question}")
#     print(f"[Detected] {language_name}")
#     print(f"[English] {search_query}")
#     # Step 2: Embed the English query and retrieve top-k chunks
#     query_embedding = get_query_embedding(search_query)

#     conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
#     cur = conn.cursor()

#     cur.execute("""
#         SELECT text, source_name, 1 - (embedding <=> %s::vector) as score
#         FROM knowledge_base
#         ORDER BY embedding <=> %s::vector
#         LIMIT 5
#     """, (str(query_embedding), str(query_embedding)))

#     rows = cur.fetchall()
#     cur.close()
#     conn.close()

#     # Step 3: Filter by minimum relevance score
#     if not rows or rows[0][2] < 0.55:
#         return {
#             "answer": (
#                 "I don't have enough reliable information to answer that confidently. "
#                 "Please consult a qualified healthcare provider or visit your nearest health facility."
#             ),
#             "score": 0.0,
#             "sources": []
#         }

#     context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
#     sources = list(set([row[1] for row in rows]))
#     best_score = float(rows[0][2])

#     # Step 4: Build system prompt
#     system_instruction = (
#         f"You are HealthBridge, a warm, knowledgeable, and attentive community health companion "
#         f"You serve users across Nigeria, Ghana, Ethiopia, and Kenya.\n\n"
#         f"Detected language: {language_name}\n"
#         f"You MUST answer entirely in {language_name}.\n"
#         f"Never switch to English unless the user explicitly requests English.\n"
#         f"LANGUAGE RULES:\n"
#             f"- Answer entirely in {language_name}.\n"
#             f"- Continue using the user's current language throughout the conversation.\n"
#             f"- If the user changes language, follow the new language.\n"
#             f"- If the user mixes languages, use the dominant language from the latest message.\n"
#             f"- Do not automatically switch to English.\n"
#             f"- Keep disease names and medical terms natural for the user's language.\n\n"
#         f"Your knowledge covers: malaria, typhoid, cholera, tuberculosis, HIV/AIDS, lassa fever, "
#         f"meningitis, dengue fever, measles, chickenpox, mpox/monkeypox, scabies, ringworm, eczema, "
#         f"conjunctivitis, jaundice, malnutrition, hypertension, diabetes, sickle cell disease, "
#         f"schistosomiasis/bilharzia, maternal and neonatal health, and more.\n\n"

#         f"Behave like a caring community health worker:\n"
#         f"- Acknowledge what the person said before answering, so they feel heard.\n"
#         f"- Ask clarifying questions when a concern is vague — for example, if someone says "
#         f"'I have a headache', ask how long, how severe, and whether there are other symptoms "
#         f"before giving advice.\n"
#         f"- Keep responses conversational and human, not clinical bullet lists, unless the user "
#         f"asks for detail or a structured explanation.\n"
#         f"- If you already have enough information from earlier in the conversation, don't ask "
#         f"the same question twice — move the conversation forward.\n"
#         f"- When a condition affects darker skin differently (e.g. eczema appearing as dark brown "
#         f"or grey patches rather than red), mention this clearly — many users may have been "
#         f"misdiagnosed because standard descriptions don't reflect how conditions look on African skin.\n"
#         f"- Always end with either a helpful next step or a gentle follow-up question.\n"
#         f"- If a symptom is a medical emergency (fever + stiff neck, convulsions, heavy bleeding, "
#         f"difficulty breathing, altered consciousness), say so clearly and urge the person to go "
#         f"to a health facility immediately — do not soften emergency guidance.\n"
#         f"- Never diagnose. Never prescribe specific medications by name without noting that a "
#         f"healthcare provider must confirm and prescribe.\n"
#         f"- Ground every factual claim in the context below. If the context doesn't cover "
#         f"something, say so honestly rather than guessing.\n\n"
#         f"Context from knowledge base:\n{context}"
#     )

#     # Step 5: Build message history and call LLM
#     messages = [{"role": "system", "content": system_instruction}]
#     for msg in history:
#         role = "assistant" if msg.get("sender") == "bot" else "user"
#         messages.append({"role": role, "content": msg.get("text", "")})
#     messages.append({"role": "user", "content": question})

#     response = client.chat.completions.create(
#         model="llama-3.3-",
#         messages=messages,
#         max_tokens=600,
#         temperature=0.3,
        
#     )
#     final_answer= response.choices[0].message.content.strip()
#     words = final_answer.split()

#     if len(words) > 20:
#         unique_ratio = len(set(words)) / len(words)

#         if unique_ratio < 0.30:
#             print("⚠ Hallucination loop detected")

#             fallback = (
#                 "I am having difficulty generating a reliable answer. "
#                 "Please try rephrasing your question."
#             )

#             return {
#                 "answer": translate_answer_to_language(
#                     fallback,
#                     language_name
#                 ),
#                 "score": best_score,
#                 "sources": sources
#             }

#     return {
#         "answer": final_answer,
#         "score": round(best_score, 4),
#         "sources": sources
#     }























"""
rag/query.py - HealthBridge Africa RAG Query Engine
Uses Gemini 2.5 Flash for generation + Gemini embeddings for retrieval
Groq Llama kept for language detection and translation
"""
import os
import psycopg2
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Gemini client - for embeddings + generation
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Groq client - ONLY for language detection + translation
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --------------------------------------------------
# LANGUAGE DETECTION + TRANSLATION (Groq - stays)
# --------------------------------------------------

def detect_language_and_translate(text: str) -> dict:
    """Detect language and translate to English using Groq Llama."""
    response = groq_client.chat.completions.create(
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
        temperature=0.0,
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
    """Translate fallback messages using Groq."""
    if language_name.lower() == "english":
        return answer

    response = groq_client.chat.completions.create(
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
# EMBEDDING (Gemini - stays same)
# --------------------------------------------------

def get_query_embedding(text: str) -> list:
    """Generate normalized 768-dim embedding for search query."""
    result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768
        )
    )
    vector = result.embeddings[0].values
    norm = sum(v * v for v in vector) ** 0.5
    normalized = [v / norm for v in vector] if norm > 0 else vector
    return normalized


# --------------------------------------------------
# MAIN RAG FUNCTION
# --------------------------------------------------

def ask_rag(question: str, language: str = "English", history: list = []) -> dict:
    """Full RAG pipeline: Gemini embeddings → pgvector search → Gemini 2.5 Flash generation."""

    # STEP 1: Detect language + translate to English for search
    detection = detect_language_and_translate(question)
    language_code = detection["language_code"]
    language_name = detection["language_name"]
    search_query = detection["english"]

    print(f"[Original]  {question}")
    print(f"[Detected]  {language_name} ({language_code})")
    print(f"[English]   {search_query}")

    # STEP 2: Embed English query + search pgvector
    query_embedding = get_query_embedding(search_query)

    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
        SELECT text, source_name, 1 - (embedding <=> %s::vector) AS score
        FROM knowledge_base
        ORDER BY embedding <=> %s::vector
        LIMIT 5
    """, (str(query_embedding), str(query_embedding)))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[Scores]    {[round(r[2], 4) for r in rows]}")

    # STEP 3: Filter by minimum relevance score
    if not rows or rows[0][2] < 0.45:
        fallback = (
            "I don't have enough reliable information to answer that confidently. "
            "Please consult a qualified healthcare provider or visit your nearest health facility."
        )
        return {
            "answer": translate_answer_to_language(fallback, language_name),
            "score": 0.0,
            "sources": [],
            "detected_language": language_code,
            "language_name": language_name
        }

    # STEP 4: Build context from retrieved chunks
    context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
    sources = list(set([row[1] for row in rows]))
    best_score = float(rows[0][2])

    # STEP 5: Build history string for Gemini system instruction
    history_text = ""
    if history:
        history_lines = []
        for msg in history[-6:]:
            role = "Assistant" if msg.get("sender") == "bot" else "User"
            history_lines.append(f"{role}: {msg.get('text', '')}")
        history_text = "\n".join(history_lines)

    # STEP 6: Build system instruction
    system_instruction = (
        f"You are HealthBridge, a warm and knowledgeable community health companion "
        f"serving users across Nigeria, Ghana, Ethiopia, and Kenya.\n\n"

        f"LANGUAGE RULES:\n"
        f"- The user speaks {language_name}. Respond ENTIRELY in {language_name}.\n"
        f"- NEVER switch to English unless the user explicitly asks for English.\n"
        f"- Never repeat the same sentence or phrase twice.\n"
        f"- If you find yourself repeating, stop and summarize in one sentence instead.\n"
        f"- Keep disease names natural in {language_name}.\n\n"

        f"TERMINOLOGY ANCHOR:\n"
        f"ወባ=malaria, ነቀርሳ=tuberculosis, ኮሌራ=cholera, ትኩሳት=fever, ተቅማጥ=diarrhea\n"
        f"busaa=malaria(Oromo), koleeraa=cholera(Oromo), dhukkuba sombaa=TB(Oromo)\n"
        f"malaria=malaria(Swahili), kifua kikuu=TB(Swahili), kipindupindu=cholera(Swahili)\n\n"

        f"BEHAVIOR RULES:\n"
        f"- Use ONLY the provided context. Never guess or invent facts.\n"
        f"- Acknowledge what the person said before answering.\n"
        f"- Ask ONE clarifying question if the concern is vague.\n"
        f"- Keep responses conversational, not clinical bullet lists.\n"
        f"- For emergency symptoms (fever + stiff neck, convulsions, heavy bleeding, "
        f"difficulty breathing), urge immediate visit to health facility — do not soften this.\n"
        f"- Never diagnose. Never prescribe specific medications.\n"
        f"- End with a helpful next step or gentle follow-up question.\n"
        f"- If context doesn't cover the question, say so honestly.\n\n"

        + (f"CONVERSATION HISTORY:\n{history_text}\n\n" if history_text else "")
        + f"CONTEXT FROM KNOWLEDGE BASE:\n{context}"
    )

    # STEP 7: Generate with Gemini 2.5 Flash
    try:
        gemini_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"{question}\n\n"
                f"(This question is about: {search_query}. "
                f"Respond entirely in {language_name}.)"
            ),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=600,
                temperature=0.3,
            )
        )
        final_answer = gemini_response.text.strip()

    except Exception as e:
        print(f"[Gemini Error] {e}")
        fallback = "I am having difficulty generating a reliable answer. Please try rephrasing your question."
        return {
            "answer": translate_answer_to_language(fallback, language_name),
            "score": best_score,
            "sources": sources,
            "detected_language": language_code,
            "language_name": language_name
        }

    # STEP 8: Hallucination loop detection
    words = final_answer.split()
    sentences = [s.strip() for s in final_answer.replace("።", ".").replace("?", ".").split(".") if s.strip()]
    word_unique_ratio = len(set(words)) / len(words) if words else 1.0
    sentence_unique_ratio = len(set(sentences)) / len(sentences) if len(sentences) > 2 else 1.0

    if len(words) > 20 and (word_unique_ratio < 0.35 or sentence_unique_ratio < 0.65):
        print("⚠ Hallucination loop detected")
        fallback = "I am having difficulty generating a reliable answer. Please try rephrasing your question."
        return {
            "answer": translate_answer_to_language(fallback, language_name),
            "score": best_score,
            "sources": sources,
            "detected_language": language_code,
            "language_name": language_name
        }

    print(f"[Score]     {round(best_score, 4)}")
    print(f"[Sources]   {sources}")

    return {
        "answer": final_answer,
        "score": round(best_score, 4),
        "sources": sources,
        "detected_language": language_code,
        "language_name": language_name
    }