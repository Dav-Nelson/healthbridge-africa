import os
import re
import psycopg2
from google import genai
from google.genai import types
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

LANGUAGE_ENFORCEMENT = {
    "English": "Respond entirely in English.",
    "Nigerian Pidgin": "You must respond ENTIRELY in Nigerian Pidgin English — every sentence, no English-only sentences mixed in, no switching back to standard English. Use natural Pidgin phrasing throughout (e.g. 'Your body dey hot' not 'Your body is hot').",
    "Swahili": "Lazima ujibu KWA KISWAHILI PEKEE — sentensi zote kwa Kiswahili, bila kuchanganya na Kiingereza. (You must respond ENTIRELY in Swahili — every sentence, no mixing in English.)",
    "Oromo": "Deebii kee guutummaatti AFAAN OROMOOTIIN kenni — sentensii hunda Afaan Oromootiin, Ingiliffa wajjin walitti hin makin. (You must respond ENTIRELY in Oromo — every sentence, no mixing in English.)",
    "Twi": "You must respond ENTIRELY in Twi — every sentence, no English-only sentences mixed in. If a medical term has no natural Twi equivalent, keep that single term in English but write the surrounding explanation in Twi.",
    "Amharic": "መልስህን ሙሉ በሙሉ በአማርኛ ስጥ — እያንዳንዱ ዓረፍተ ነገር በአማርኛ መሆን አለበት፣ ከእንግሊዝኛ ጋር አትቀላቅል። (You must respond ENTIRELY in Amharic — every sentence, no mixing in English.)"
}

# Languages where Llama-3.1-8B-Instant has demonstrated reliable, coherent output.
# Twi and Amharic are excluded from the forced re-translation pass because the
# model frequently degenerates into repetitive token loops for these languages —
# it's safer to keep the original (possibly partially English) answer than risk
# returning broken, looping text.
RELIABLE_FOR_TRANSLATION_PASS = {"Nigerian Pidgin", "Swahili", "Oromo"}


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
            if most_common_count >= 5:
                return True

    return False


def get_query_embedding(text: str) -> list:
    """Generate a normalized 768-dim embedding for a search query via Gemini."""
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
    """Full RAG: Embed query via Gemini, search Neon DB, then answer with Groq Llama 3."""

    search_query = question
    try:
        trans_res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Translate the following query strictly to English. Return ONLY the English text, nothing else."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.0
        )
        search_query = trans_res.choices[0].message.content.strip() or question
    except Exception as e:
        print(f"Translation failed: {e}")

    query_embedding = get_query_embedding(search_query)

    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
        SELECT text, source_name, 1 - (embedding <=> %s::vector) as score
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

    if not rows or rows[0][2] < 0.40:
        return {
            "answer": fallback_messages.get(language, fallback_messages["English"]),
            "score": 0.0,
            "sources": []
        }

    context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
    sources = list(set([row[1] for row in rows]))
    best_score = float(rows[0][2])

    language_rule = LANGUAGE_ENFORCEMENT.get(language, LANGUAGE_ENFORCEMENT["English"])

    system_instruction = (
        f"You are HealthBridge, a warm, knowledgeable, and attentive community health companion. "
        f"You serve users across Nigeria, Ghana, Ethiopia, and Kenya.\n\n"

        f"=== LANGUAGE REQUIREMENT — HIGHEST PRIORITY ===\n"
        f"The user's selected language is: {language}.\n"
        f"{language_rule}\n"
        f"The knowledge base context below is written in English. You must still translate "
        f"and explain all of it in {language}. Do NOT answer in English unless the selected "
        f"language is English. This rule overrides all other style preferences.\n"
        f"=================================================\n\n"

        f"=== FORMATTING REQUIREMENT ===\n"
        f"Write in plain conversational text only. Do NOT use markdown formatting — no asterisks "
        f"for bold or italics, no # headers, no bullet point markers. If you need to list items, "
        f"write them as a natural sentence or use simple numbered lines like '1. ', '2. ' without "
        f"any asterisks or symbols.\n"
        f"=================================================\n\n"

        f"Your knowledge covers: malaria, typhoid, cholera, tuberculosis, HIV/AIDS, lassa fever, "
        f"meningitis, dengue fever, measles, chickenpox, mpox/monkeypox, scabies, ringworm, eczema, "
        f"conjunctivitis, jaundice, malnutrition, hypertension, diabetes, sickle cell disease, "
        f"schistosomiasis/bilharzia, maternal and neonatal health, and more.\n\n"

        f"Behave like a caring community health worker:\n"
        f"- Acknowledge what the person said before answering, so they feel heard.\n"
        f"- Ask clarifying questions when a concern is vague — for example, if someone says "
        f"'I have a headache', ask how long, how severe, and whether there are other symptoms "
        f"before giving advice.\n"
        f"- Keep responses conversational and human, not clinical bullet lists, unless the user "
        f"asks for detail or a structured explanation.\n"
        f"- If you already have enough information from earlier in the conversation, don't ask "
        f"the same question twice — move the conversation forward.\n"
        f"- When a condition affects darker skin differently (e.g. eczema appearing as dark brown "
        f"or grey patches rather than red), mention this clearly — many users may have been "
        f"misdiagnosed because standard descriptions don't reflect how conditions look on African skin.\n"
        f"- Always end with either a helpful next step or a gentle follow-up question.\n"
        f"- If a symptom is a medical emergency (fever + stiff neck, convulsions, heavy bleeding, "
        f"difficulty breathing, altered consciousness), say so clearly and urge the person to go "
        f"to a health facility immediately — do not soften emergency guidance.\n"
        f"- Never diagnose. Never prescribe specific medications by name without noting that a "
        f"healthcare provider must confirm and prescribe.\n"
        f"- Ground every factual claim in the context below. If the context doesn't cover "
        f"something, say so honestly rather than guessing.\n\n"
        f"Context from knowledge base:\n{context}\n\n"
        f"=== FINAL REMINDER ===\n"
        f"{language_rule}\n"
        f"Remember: no markdown, no asterisks, plain conversational text only."
    )

    messages = [{"role": "system", "content": system_instruction}]
    for msg in history:
        role = "assistant" if msg.get("sender") == "bot" else "user"
        messages.append({"role": role, "content": msg.get("text", "")})
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=600,
        temperature=0.3
    )

    answer = response.choices[0].message.content

    # Safety check: if the initial generation is already degenerate, fall back immediately
    if is_degenerate(answer):
        print(f"Degenerate output detected on initial generation for language={language}")
        answer = fallback_messages.get(language, fallback_messages["English"])
        return {"answer": answer, "score": round(best_score, 4), "sources": sources}

    # Only run the extra translation/cleanup pass for languages where Llama
    # has shown reliable output. Twi and Amharic skip this — too high a risk
    # of degenerate loops, and the original answer (cleaned of markdown) is safer.
    if language in RELIABLE_FOR_TRANSLATION_PASS:
        try:
            verify_res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": (
                        f"You are a strict language checker and translator. The text below is "
                        f"supposed to be written entirely in {language}, in plain text with no "
                        f"markdown formatting. If it already meets both requirements, return it "
                        f"completely unchanged. If any part is in English (when it shouldn't be) "
                        f"or contains markdown symbols like asterisks or hashtags, fix it: "
                        f"translate fully into natural, fluent {language} and strip all markdown. "
                        f"Return ONLY the final plain text in {language}, nothing else."
                    )},
                    {"role": "user", "content": answer}
                ],
                max_tokens=700,
                temperature=0.0
            )
            corrected = verify_res.choices[0].message.content.strip()
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
        "sources": sources
    }