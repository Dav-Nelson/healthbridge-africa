import os
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

    # Step 1: Translate query to English for better semantic search
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

    # Step 2: Embed the English query and retrieve top-k chunks
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

    # Step 3: Filter by minimum relevance score
    if not rows or rows[0][2] < 0.40:
        return {
            "answer": (
                "I don't have enough reliable information to answer that confidently. "
                "Please consult a qualified healthcare provider or visit your nearest health facility."
            ),
            "score": 0.0,
            "sources": []
        }

    context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
    sources = list(set([row[1] for row in rows]))
    best_score = float(rows[0][2])

    # Step 4: Build system prompt
    system_instruction = (
        f"You are HealthBridge, a warm, knowledgeable, and attentive community health companion "
        f"speaking with someone in {language}. You serve users across Nigeria, Ghana, Ethiopia, and Kenya.\n\n"

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
        f"Context from knowledge base:\n{context}"
    )

    # Step 5: Build message history and call LLM
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

    return {
        "answer": response.choices[0].message.content,
        "score": round(best_score, 4),
        "sources": sources
    }