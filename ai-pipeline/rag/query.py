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
            "answer": f"I'm not fully certain about that in the HealthBridge knowledge base. Please consult a healthcare professional.",
            "score": 0.0,
            "sources": []
        }

    # 4. Construct Context
    context = "\n\n".join([f"[Source: {row[1]}]\n{row[0]}" for row in rows])
    sources = list(set([row[1] for row in rows]))
    best_score = float(rows[0][2])

    # 5. LLM Response Generation
    system_instruction = (
        f"You are a warm, professional health assistant. Answer in {language}. "
        f"Use the context provided as your primary source of truth.\n\nContext:\n{context}"
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