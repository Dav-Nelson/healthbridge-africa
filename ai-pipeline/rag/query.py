"""
rag/query.py - HealthBridge Africa RAG Query Engine
Uses Gemini 2.5 Flash for generation + Gemini embeddings for retrieval
Groq Llama-3.3-70b kept for language detection and translation only
"""
import os
import re
import psycopg2
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Gemini client — embeddings + generation
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# Groq client — language detection + translation only
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LANGUAGE_ENFORCEMENT = {
    "English": "Respond entirely in English.",
    "Nigerian Pidgin": "You must respond ENTIRELY in Nigerian Pidgin English — every sentence, no English-only sentences mixed in, no switching back to standard English. Use natural Pidgin phrasing throughout (e.g. 'Your body dey hot' not 'Your body is hot').",
    "Swahili": "Lazima ujibu KWA KISWAHILI PEKEE — sentensi zote kwa Kiswahili, bila kuchanganya na Kiingereza. (You must respond ENTIRELY in Swahili — every sentence, no mixing in English.)",
    "Oromo": "Deebii kee guutummaatti AFAAN OROMOOTIIN kenni — sentensii hunda Afaan Oromootiin, Ingiliffa wajjin walitti hin makin. (You must respond ENTIRELY in Oromo — every sentence, no mixing in English.)",
    "Twi": "You must respond ENTIRELY in Twi — every sentence, no English-only sentences mixed in. If a medical term has no natural Twi equivalent, keep that single term in English but write the surrounding explanation in Twi.",
    "Amharic": "መልስህን ሙሉ በሙሉ በአማርኛ ስጥ — እያንዳንዱ ዓረፍተ ነገር በአማርኛ መሆን አለበት፣ ከእንግሊዝኛ ጋር አትቀላቅል። (You must respond ENTIRELY in Amharic — every sentence, no mixing in English.)"
}

# Only run verification pass for languages where the model is reliable.
# Twi, Amharic, and Oromo are excluded — too high a risk of degenerate loops.
RELIABLE_FOR_TRANSLATION_PASS = {"Nigerian Pidgin", "Swahili"}

# Fallback messages in all supported languages
FALLBACK_MESSAGES = {
    "English": "I don't have enough reliable information to answer that confidently. Please consult a qualified healthcare provider or visit your nearest health facility.",
    "Nigerian Pidgin": "I no get enough correct information to answer dat question well well. Abeg go see correct doctor or visit di health center near you.",
    "Swahili": "Sina taarifa za kutosha kujibu swali hilo kwa uhakika. Tafadhali wasiliana na mtaalamu wa afya au tembelea kituo cha afya kilicho karibu nawe.",
    "Oromo": "Gaaffii kanaaf deebii sirrii kennuuf odeeffannoo ga'aa hin qabu. Maaloo ogeessa fayyaa mariisisi yookaan dhaabbata fayyaa naannoo keessanitti argamu daawwadhaa.",
    "Twi": "Minni nsɛm a edi mu pii a mede bɛyi saa asɛmmisa yi ano yiye. Yɛsrɛ wo, kɔ hwɛ oduruyɛfo anaa kɔ ayaresabea a ɛbɛn wo.",
    "Amharic": "ለዚህ ጥያቄ በትክክል ለመመለስ በቂ መረጃ የለኝም። እባክዎ ብቁ የጤና ባለሙያ ያማክሩ ወይም በአቅራቢያዎ ወዳለው የጤና ተቋም ይሂዱ።"
}


def strip_markdown(text: str) -> str:
    """Remove markdown formatting so plain-text frontends render cleanly."""
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
    """Detect repetitive/looping model output that should never reach the user."""
    if not text or len(text) < 10:
        return False

    # Character-level check: catches glued fragments like "nkyɛnkyɛnkyɛn..."
    for frag_len in (3, 4, 5, 6):
        if len(text) < frag_len * 8:
            continue
        for start in range(0, min(len(text) - frag_len * 6, 50)):
            fragment = text[start:start + frag_len]
            if not fragment.strip():
                continue
            if fragment * 6 in text:
                return True

    words = text.split()
    if len(words) < 8:
        return False

    # Word-level: small unique word set dominating response
    unique_words = set(words)
    if len(unique_words) / len(words) < 0.25:
        return True

    # Phrase-level: same short phrase repeating many times
    for phrase_len in (3, 4, 5):
        if len(words) < phrase_len * 4:
            continue
        phrases = [' '.join(words[i:i + phrase_len]) for i in range(len(words) - phrase_len)]
        if phrases:
            most_common_count = max(phrases.count(p) for p in set(phrases))
            if most_common_count >= 5:
                return True

    # Sentence-level: catches Amharic/Oromo compound word loops
    sentences = [s.strip() for s in re.split(r'[.?።]', text) if s.strip()]
    if len(sentences) > 2:
        sentence_unique_ratio = len(set(sentences)) / len(sentences)
        if sentence_unique_ratio < 0.65:
            return True

    # Extremely long single token with no spaces = glued repetition blob
    longest_word = max((len(w) for w in words), default=0)
    if longest_word > 80:
        return True

    return False


def detect_language_and_translate(text: str) -> dict:
    """Detect language and translate to English using Groq Llama-3.3-70b."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a medical language detector and translator.

TASK:
1. Detect the language of the input.
2. Translate it to English.

IMPORTANT MEDICAL TERMS:

AMHARIC: ወባ=malaria, ኮሌራ=cholera, ነቀርሳ=tuberculosis, ትኩሳት=fever, ተቅማጥ=diarrhea, የራስ ህመም=headache
OROMO: busaa=malaria, koleeraa=cholera, dhukkuba sombaa=tuberculosis, hoo'a qaamaa=fever, garaa kaasaa=diarrhea
SWAHILI: malaria=malaria, kipindupindu=cholera, kifua kikuu=tuberculosis, homa=fever, kuhara=diarrhea
PIDGIN: body dey hot=fever, running stomach=diarrhea, head dey pain me=headache
TWI: atiridii=malaria, tirim=headache

Language codes: am=Amharic, om=Oromo, sw=Swahili, pcm=Nigerian Pidgin, tw=Twi, en=English

Respond EXACTLY in this format:
LANGUAGE_CODE: code
LANGUAGE_NAME: name
ENGLISH: translation"""
                },
                {"role": "user", "content": text}
            ],
            temperature=0.0,
            max_tokens=150
        )
        content = response.choices[0].message.content.strip()
        result = {"language_code": "en", "language_name": "English", "english": text}
        for line in content.split("\n"):
            if line.startswith("LANGUAGE_CODE:"):
                result["language_code"] = line.split(":", 1)[1].strip().lower()
            elif line.startswith("LANGUAGE_NAME:"):
                result["language_name"] = line.split(":", 1)[1].strip()
            elif line.startswith("ENGLISH:"):
                result["english"] = line.split(":", 1)[1].strip()
        return result
    except Exception as e:
        print(f"Language detection failed: {e}")
        return {"language_code": "en", "language_name": "English", "english": text}


def get_query_embedding(text: str) -> list:
    """Generate normalized 768-dim embedding for search query via Gemini."""
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


def ask_rag(question: str, language: str = "English", history: list = []) -> dict:
    """Full RAG pipeline: detect language → embed → retrieve → generate with Gemini 2.5 Flash."""

    # Step 1: Detect language and translate to English for search
    detection = detect_language_and_translate(question)
    language_code = detection["language_code"]
    language_name = detection["language_name"]
    search_query = detection["english"]

    # Use the language passed from the frontend as the authoritative response language
    # (detection is used for search only — the user's UI selection determines response language)
    response_language = language if language != "English" or language_name == "English" else language_name

    print(f"[Original]  {question}")
    print(f"[Detected]  {language_name} ({language_code})")
    print(f"[Search]    {search_query}")
    print(f"[Respond]   {response_language}")

    # Step 2: Embed English query and retrieve top-5 chunks from pgvector
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

    # Step 3: Filter by minimum relevance score
    if not rows or rows[0][2] < 0.30:
        return {
            "answer": FALLBACK_MESSAGES.get(response_language, FALLBACK_MESSAGES["English"]),
            "score": 0.0,
            "sources": []
        }

    context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
    sources = list(set([row[1] for row in rows]))
    best_score = float(rows[0][2])

    # Step 4: Build conversation history string
    history_text = ""
    if history:
        history_lines = []
        for msg in history[-6:]:
            role = "Assistant" if msg.get("sender") == "bot" else "User"
            history_lines.append(f"{role}: {msg.get('text', '')}")
        history_text = "\n".join(history_lines)

    # Step 5: Build system prompt
    language_rule = LANGUAGE_ENFORCEMENT.get(response_language, LANGUAGE_ENFORCEMENT["English"])

    system_instruction = (
        f"You are HealthBridge, a warm and knowledgeable community health companion "
        f"serving users across Nigeria, Ghana, Ethiopia, and Kenya.\n\n"

        f"=== LANGUAGE REQUIREMENT — HIGHEST PRIORITY ===\n"
        f"The user's selected language is: {response_language}.\n"
        f"{language_rule}\n"
        f"The knowledge base context is in English. Translate and explain everything in {response_language}.\n"
        f"Do NOT respond in English unless the selected language is English.\n"
        f"Never switch languages mid-response.\n"
        f"Never repeat the same sentence twice — if you catch yourself repeating, summarize instead.\n"
        f"=================================================\n\n"

        f"=== FORMATTING ===\n"
        f"Write in plain conversational text only. No markdown — no asterisks, no # headers, "
        f"no bullet point markers. If listing items, use natural sentences or simple numbered "
        f"lines like '1. ', '2. ' without symbols.\n"
        f"=================================================\n\n"

        f"=== TERMINOLOGY ANCHORS ===\n"
        f"ወባ = malaria | ነቀርሳ = tuberculosis | ኮሌራ = cholera | ትኩሳት = fever | ተቅማጥ = diarrhea\n"
        f"busaa = malaria | koleeraa = cholera | dhukkuba sombaa = tuberculosis\n"
        f"kifua kikuu = tuberculosis | kipindupindu = cholera | homa = fever\n"
        f"=================================================\n\n"

        f"=== BEHAVIOR ===\n"
        f"- Acknowledge what the person said before answering so they feel heard.\n"
        f"- Ask clarifying questions when a concern is vague.\n"
        f"- Keep responses conversational and human, not clinical bullet lists.\n"
        f"- When a condition appears differently on darker skin (e.g. eczema as dark brown or "
        f"grey patches rather than red), mention this — many users have been misdiagnosed.\n"
        f"- If symptoms suggest an emergency (fever with stiff neck, convulsions, heavy bleeding, "
        f"difficulty breathing, altered consciousness), say so clearly and urge immediate care.\n"
        f"- Never diagnose. Never prescribe medications by name without noting a provider must confirm.\n"
        f"- Ground every factual claim in the context below. If context doesn't cover something, "
        f"say so honestly rather than guessing.\n"
        f"- End with a helpful next step or gentle follow-up question.\n\n"

        + (f"=== CONVERSATION HISTORY ===\n{history_text}\n\n" if history_text else "")
        + f"=== CONTEXT FROM KNOWLEDGE BASE ===\n{context}\n\n"

        f"=== FINAL REMINDER ===\n"
        f"{language_rule}\n"
        f"No markdown. No asterisks. Plain conversational text only."
    )

    # Step 6: Generate with Gemini 2.5 Flash
    try:
        gemini_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"{question}\n\n"
                f"(English meaning: {search_query}. Respond entirely in {response_language}.)"
            ),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=1500,
                temperature=0.3,
            )
        )
        answer = gemini_response.text.strip()
    except Exception as e:
        print(f"[Gemini generation error] {e}")
        return {
            "answer": FALLBACK_MESSAGES.get(response_language, FALLBACK_MESSAGES["English"]),
            "score": best_score,
            "sources": sources
        }

    # Step 7: Safety check — catch degenerate output immediately
    if is_degenerate(answer):
        print(f"Degenerate output detected on initial generation for language={response_language}")
        return {
            "answer": FALLBACK_MESSAGES.get(response_language, FALLBACK_MESSAGES["English"]),
            "score": round(best_score, 4),
            "sources": sources
        }

    # Step 8: Verification pass for reliable languages only
    if response_language in RELIABLE_FOR_TRANSLATION_PASS:
        try:
            verify_res = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    f"You are a strict language checker. The text below must be entirely in "
                    f"{response_language} with no markdown formatting.\n\n"
                    f"If it is already correct, return it unchanged.\n"
                    f"If it contains English or markdown, fix it.\n"
                    f"Return ONLY the corrected plain text.\n\n"
                    f"Text:\n{answer}"
                ),
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=900,
                )
            )
            corrected = verify_res.text.strip()
            if corrected and not is_degenerate(corrected):
                answer = corrected
            else:
                print(f"Verification pass produced degenerate output, keeping original")
        except Exception as e:
            print(f"Verification pass failed: {e}")

    # Step 9: Strip any remaining markdown
    answer = strip_markdown(answer)

    # Step 10: Final safety net
    if is_degenerate(answer):
        answer = FALLBACK_MESSAGES.get(response_language, FALLBACK_MESSAGES["English"])

    print(f"[Score]   {round(best_score, 4)}")
    print(f"[Sources] {sources}")

    return {
        "answer": answer,
        "score": round(best_score, 4),
        "sources": sources
    }