import os
import psycopg2
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
model = SentenceTransformer("all-MiniLM-L6-v2")

def ask_rag(question: str, language: str = "English", history: list = []) -> dict:
    """Full RAG: Embed query, search Neon DB, then answer with Groq Llama 3."""
    
    # 1. Translate query to English for consistent vector search
    search_query = question
    try:
        trans_res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Translate the query strictly to English. Return ONLY the English text."},
                {"role": "user", "content": question}
            ],
            max_tokens=100,
            temperature=0.0
        )
        search_query = trans_res.choices[0].message.content.strip() or question
    except Exception as e:
        print(f"Translation failed: {e}")

    # 2. Vector Search in Neon DB
    query_embedding = model.encode(search_query).tolist()
    
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    cur = conn.cursor()
    
    cur.execute("""
        SELECT text, source_name, 1 - (embedding <=> %s::vector) as score 
        FROM knowledge_base 
        ORDER BY embedding <=> %s::vector 
        LIMIT 3
    """, (str(query_embedding), str(query_embedding)))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # 3. Handle Empty Results
    if not rows or rows[0][2] < 0.45:
        return {
            "answer": "I don't have enough reliable information to answer that confidently. Please consult a healthcare professional.",
            "score": 0.0,
            "sources": []
        }

    # 4. Construct Context
    context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
    sources = list(set([row[1] for row in rows]))
    best_score = float(rows[0][2])

    # 5. LLM Response Generation
    system_instruction = (
        f"You are HealthBridge, a warm and attentive health companion speaking with someone in {language}. "
        f"You are not a search engine — you are having a real conversation.\n\n"
        f"Behave like a caring community health worker would:\n"
        f"- Ask clarifying questions when the user's concern is vague or could mean several things "
        f"(e.g. if they say 'I have a headache', ask how long, how severe, or if there are other symptoms before giving advice).\n"
        f"- Acknowledge what the person said before answering, so they feel heard.\n"
        f"- Keep responses conversational and human, not clinical lists, unless the user asks for detail.\n"
        f"- If you already have enough information from earlier in the conversation, don't ask the same thing twice — move the conversation forward.\n"
        f"- Always end with either a helpful next step or a gentle follow-up question, never a flat full stop.\n\n"
        f"Ground every factual claim in the context below. If the context doesn't cover something, say so honestly "
        f"rather than guessing.\n\nContext:\n{context}"
    )
    
    messages = [{"role": "system", "content": system_instruction}]
    for msg in history:
        role = "assistant" if msg.get("sender") == "bot" else "user"
        messages.append({"role": role, "content": msg.get("text", "")})
    
    messages.append({"role": "user", "content": question})
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=500,
        temperature=0.3
    )
    
    return {
        "answer": response.choices[0].message.content,
        "score": round(best_score, 4),
        "sources": sources
    }