# ai-pipeline/rag/query.py
"""
RAG query pipeline:
1. Embed the user question (sentence-transformers, local)
2. Search vector_store.json for best matching chunks
3. Send question + context to Groq (Llama 3) for grounded answer
"""
import os
import json
import numpy as np
from groq import Groq
from dotenv import load_dotenv

# load_dotenv(dotenv_path="ai-pipeline/.env")
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load embedding model once (reused across calls)
from sentence_transformers import SentenceTransformer
_embed_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list:
    return _embed_model.encode(text).tolist()


def cosine_similarity(a, b) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search_documents(question: str, top_k: int = 3) -> list:
    """Find the top_k most relevant chunks for a question."""
    
    # store_path = "ai-pipeline/docs/vector_store.json"
    
    store_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "docs",
    "vector_store.json"
    )
    
    if not os.path.exists(store_path):
        raise FileNotFoundError(
            "vector_store.json not found. Run ingest.py first."
        )
    
    with open(store_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    query_embedding = embed_text(question)
    
    # Score every chunk
    scored = []
    for doc in documents:
        score = cosine_similarity(query_embedding, doc["embedding"])
        scored.append({**doc, "score": score})
    
    # Return top_k results sorted by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def ask_rag(question: str) -> dict:
    """Full RAG: search knowledge base, then answer with Groq Llama 3."""
    
    top_chunks = search_documents(question, top_k=3)
    best_score = top_chunks[0]["score"]

    if best_score < 0.45:
        return {
            "answer": (
                "I could not find reliable information in the "
                "HealthBridge knowledge base for that question. "
                "Please consult a healthcare professional."
            ),
            "context": "",
            "score": round(best_score, 4),
            "sources": []
        }
    if not top_chunks:
        return {
            "answer": "I don't have verified information on that. Please consult a healthcare provider.",
            "context": "",
            "score": 0
        }
    
    # Build context from top chunks
    context_parts = []
    for chunk in top_chunks:
        context_parts.append(
            f"[Source: {chunk.get('source', 'Health Document')}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)
    
    context = context[:6000]
    # Call Groq (Llama 3) — fast, free, cloud-based
    # response = client.chat.completions.create(
    #     model="llama3-8b-8192",   # Free Llama 3 on Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                "You are HealthBridge Africa's health information assistant. "
                "Use ONLY the supplied context. "
                "Never diagnose diseases. "
                "Never prescribe medication. "
                "Never invent medical information. "
                "If the answer is not in the context, say so clearly. "
                "Always recommend professional medical care when symptoms are severe or persistent. "
                "Keep responses simple and easy to understand."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ],
        max_tokens=500,
        temperature=0.3   # Low temperature = more factual, less creative
    )
    
    return {
        "answer": response.choices[0].message.content,
        "context": context,
        "score": round(top_chunks[0]["score"], 4),
        "sources": [c.get("source", "unknown") for c in top_chunks]
    }


if __name__ == "__main__":
    result = ask_rag("What are the symptoms of malaria and when should I see a doctor?")
    print("\n=== HealthBridge Africa Answer ===")
    print(result["answer"])
    print(f"\nTop similarity score: {result['score']}")
    print(f"Sources used: {result['sources']}")
    