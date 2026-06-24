
"""
rag/query.py - HealthBridge Africa RAG Query Engine
Uses Gemini 2.5 Flash for generation + Gemini embeddings for retrieval
Groq Llama kept for language detection and translation
"""
import os
import re
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

LANGUAGE_ENFORCEMENT = {
    "English": "Respond entirely in English.",
    "Nigerian Pidgin": "You must respond ENTIRELY in Nigerian Pidgin English — every sentence, no English-only sentences mixed in, no switching back to standard English. Use natural Pidgin phrasing throughout (e.g. 'Your body dey hot' not 'Your body is hot').",
    "Swahili": "Lazima ujibu KWA KISWAHILI PEKEE — sentensi zote kwa Kiswahili, bila kuchanganya na Kiingereza. (You must respond ENTIRELY in Swahili — every sentence, no mixing in English.)",
    "Oromo": "Deebii kee guutummaatti AFAAN OROMOOTIIN kenni —senteensii hunda Afaan Oromootiin deebisi, Ingiliffa wajjin walitti hin makiin. (You must respond ENTIRELY in Oromo — every sentence, no mixing in English.)",
    "Twi": "You must respond ENTIRELY in Twi — every sentence, no English-only sentences mixed in. If a medical term has no natural Twi equivalent, keep that single term in English but write the surrounding explanation in Twi.",
    "Amharic": "መልስህን ሙሉ በሙሉ በአማርኛ ስጥ — እያንዳንዱ ዓረፍተ ነገር በአማርኛ መሆን አለበት፣ ከእንግሊዝኛ ጋር አትቀላቅል። (You must respond ENTIRELY in Amharic — every sentence, no mixing in English.)"
}

# Languages where Llama-3.1-8B-Instant has demonstrated reliable, coherent output.
RELIABLE_FOR_TRANSLATION_PASS = {"Nigerian Pidgin", "Swahili"}


def strip_markdown(text: str) -> str:
    """Remove markdown formatting characters so plain-text frontends render cleanly."""
    if not text:
        return text
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\*\-]\s+', '', text, flags=re.MULTILINE)
    return text.strip()

def is_degenerate(text: str) -> bool:
    """Detect repetitive/looping model output that should never be shown to a user."""
    if not text or len(text) < 10:
        return False

    words = text.split()
    if len(words) < 8:
        return False

    # Check if a small set of words dominates the response (repetition loop)
    unique_words = set(words)
    if len(unique_words) / len(words) < 0.25:
        return True

    # Check if the same short phrase (3-5 words) repeats many times in a row
    for phrase_len in (3, 4, 5):
        if len(words) < phrase_len * 4:
            continue

        phrases = [' '.join(words[i:i + phrase_len]) for i in range(len(words) - phrase_len)]

        if phrases:
            most_common_count = max(phrases.count(p) for p in set(phrases))
            if most_common_count >= 4:
                return True

    return False


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
    try:
        content = response.choices[0].message.content.strip()
    except Exception:
        return{
            "language_code": "en",
            "language_name": "English",
            "english": text,
        }
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

def translate_answer_to_language(answer: str, language_name: str):
    if language_name.lower() == "english":
        return answer

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"Translate the following health message into {language_name}. "
                "Preserve the medical meaning exactly. "
                "Return ONLY the translation.\n\n"
                f"{answer}"
            ),
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=300,
            ),
        )

        return response.text.strip()

    except Exception as e:
        print (f"Translation Error {e}")
        return answer

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


    fallback_messages = {
        "English": "I don't have enough reliable information to answer that confidently. Please consult a qualified healthcare provider or visit your nearest health facility.",
        "Nigerian Pidgin": "I no get enough correct information to answer dat question well well. Abeg go see correct doctor or visit di health center near you.",
        "Swahili": "Sina taarifa za kutosha kujibu swali hilo kwa uhakika. Tafadhali wasiliana na mtaalamu wa afya au tembelea kituo cha afya kilicho karibu nawe.",
        "Oromo": "Gaaffii kanaaf deebii sirrii kennuuf odeeffannoo ga'aa hin qabu. Maaloo ogeessa fayyaa mariisisi yookaan dhaabbata fayyaa naannoo keessanitti argamu daawwadhaa.",
        "Twi": "Minni nsɛm a edi mu pii a mede bɛyi saa asɛmmisa yi ano yiye. Yɛsrɛ wo, kɔ hwɛ oduruyɛfo anaa kɔ ayaresabea a ɛbɛn wo.",
        "Amharic": "ለዚህ ጥያቄ በትክክል ለመመለስ በቂ መረጃ የለኝም። እባክዎ ብቁ የጤና ባለሙያ ያማክሩ ወይም በአቅራቢያዎ ወዳለው የጤና ተቋም ይሂዱ።"
    }

    if not rows or rows[0][2] < 0.45:
        return {
            "answer": fallback_messages.get(language_name, fallback_messages["English"]),
            "score": 0.0,
            "sources": [],
            "detected_language": language_code,
            "language_name": language_name
        }

    # STEP 4: Build context from retrieved chunks
    context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
    sources = list(set([row[1] for row in rows]))
    best_score = float(rows[0][2])

# STEP 5: Build history string
    history_text = ""
    if history:
        history_lines = []
        for msg in history[-6:]:
            role = "Assistant" if msg.get("sender") == "bot" else "User"
            history_lines.append(f"{role}: {msg.get('text', '')}")
        history_text = "\n".join(history_lines)

    # STEP 6: Build system instruction
    language_rule = LANGUAGE_ENFORCEMENT.get(language_name, LANGUAGE_ENFORCEMENT["English"])

    system_instruction = (
        f"You are HealthBridge, a warm and knowledgeable community health companion "
        f"serving users across Nigeria, Ghana, Ethiopia, and Kenya.\n\n"

        f"LANGUAGE RULES:\n"
        f"{language_rule}\n"
        f"This rule has the highest priority.\n" 
        f"- Never switch to English unless the user explicitly asks.\n"
        f"- Never repeat the same sentence twice.\n"
        f"- If you find yourself repeating, summarize instead.\n\n"

        f"TERMINOLOGY ANCHOR:\n"
        f"ወባ = malaria\n"
        f"ነቀርሳ = tuberculosis\n"
        f"ኮሌራ = cholera\n"
        f"ትኩሳት = fever\n"
        f"ተቅማጥ = diarrhea\n"
        f"busaa = malaria\n"
        f"koleeraa = cholera\n"
        f"dhukkuba sombaa = tuberculosis\n"
        f"malaria = malaria\n"
        f"kifua kikuu = tuberculosis\n"
        f"kipindupindu = cholera\n\n"

        f"BEHAVIOR RULES:\n"
        f"- Use ONLY the provided context.\n"
        f"- Never invent facts.\n"
        f"- Start answering immediately.\n"
        f"- Never repeat or rewrite the user's question.\n"
        f"- Do not begin with 'Thank you for your question'.\n"
        f"- Avoid unnecessary introductions.\n"
        f"- Ask ONE clarifying question if needed.\n"
        f"- Keep responses conversational.\n"
        f"- Never diagnose.\n"
        f"- Never prescribe medications.\n"
        f"- Keep answers concise."
        f"- Use short paragraphs."
        f"- Avoid repeating information."
        f"- Do not explain obvious things unless the user asks."
        f"- If symptoms suggest an emergency (difficulty breathing, heavy bleeding, convulsions, fever with stiff neck), clearly advise immediate medical care.\n"
        f"- End with a helpful next step or follow-up question.\n"
        f"- If the context doesn't contain the answer, say so honestly.\n\n"

        + (f"CONVERSATION HISTORY:\n{history_text}\n\n" if history_text else "")
        + f"CONTEXT FROM KNOWLEDGE BASE:\n{context}"
        f"- Keep answers concise."
        f"- Use short paragraphs."
        f"- Avoid repeating information."
        f"- Do not explain obvious things unless the user asks."
    )
    

    # STEP 7: Generate with Gemini 2.5 Flash
    try:
        gemini_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            # contents=question,
            contents=(
                f"{question}\n\n"
                f"(This question is about: {search_query}. "
                f"Respond entirely in {language_name}.)"
            ),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=2000,
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
    
    # Safety check: if the initial generation is already degenerate, fall back immediately
    answer = final_answer
    if is_degenerate(answer):
        print(f"Degenerate output detected on initial generation for language={language}")
        answer = fallback_messages.get(language, fallback_messages["English"])
        return {"answer": answer, "score": round(best_score, 4), "sources": sources}

    # Only run the extra translation/cleanup pass for languages where Llama
    # has shown reliable output. Twi and Amharic skip this — too high a risk
    # of degenerate loops, and the original answer (cleaned of markdown) is safer.
    if language in RELIABLE_FOR_TRANSLATION_PASS:
        try:
            verify_res = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
            You are a strict language checker and translator.

            The following text must be entirely in {language_name}.

            If it is already correct, return it unchanged.

            If it contains English, translate it.

            Remove markdown.

            Return ONLY the corrected text.

            Text:

            {answer}
            """,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=1400,
                ),
            )

            corrected = verify_res.text.strip()
            if corrected and not is_degenerate(corrected):
                answer = corrected
            elif is_degenerate(corrected):
                print(f"Degenerate output detected on verification pass for language={language}, keeping original")
        except Exception as e:
            print(f"Language enforcement pass failed: {e}")

    answer = strip_markdown(answer)

    # Final safety net — if somehow still degenerate after all processing, use fallback
    if is_degenerate(answer):
        answer = fallback_messages.get(language, fallback_messages["English"])

    return {
        "answer": answer,

        "score": round(best_score, 4),
        "sources": sources,
        "detected_language": language_code,
        "language_name": language_name
    }