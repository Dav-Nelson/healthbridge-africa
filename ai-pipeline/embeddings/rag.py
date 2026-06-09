# embeddings/rag.py
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict
import os

from embeddings.search import search

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MIN_SIMILARITY = 0.25


def ask(question: str, history: List[Dict] = []) -> dict:
    """Full RAG pipeline with conversation memory."""

    # Step 1: Search pgvector
    results = search(question, top_k=5)

    # Step 2: Filter relevant chunks
    relevant = [r for r in results if r["similarity"] >= MIN_SIMILARITY]

    if not relevant:
        return {
            "answer": (
                "I could not find relevant health information for that question. "
                "Please consult a qualified healthcare provider."
            ),
            "sources": [],
            "score":   0.0
        }

    # Step 3: Build context
    context_parts = []
    for r in relevant:
        context_parts.append(
            f"[Source: {r['source']} | Condition: {r.get('condition', 'general')}]\n"
            f"{r['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)
    context = context[:6000]

    # Step 4: Build messages with history
    messages = [
        {
            "role": "system",
            "content": (
                "You are HealthBridge Africa's health information assistant "
                "serving communities across Africa.\n\n"
                "RULES:\n"
                "1. Use ONLY the context provided below to answer.\n"
                "2. Never diagnose diseases.\n"
                "3. Never prescribe specific medications.\n"
                "4. If the answer is not in the context, say clearly: "
                "'I don't have that information in my knowledge base.'\n"
                "5. Always recommend professional medical care for "
                "severe or persistent symptoms.\n"
                "6. If the user's question refers to something from earlier "
                "in the conversation (like 'its treatment' or 'how to prevent it'), "
                "use the conversation history to understand what 'it' refers to.\n"
                "7. Keep responses simple and easy to understand.\n\n"
                f"CONTEXT:\n{context}"
            )
        }
    ]

    # Add last 6 messages from history
    for msg in history[-6:]:
        messages.append({
            "role":    msg["role"],
            "content": msg["content"]
        })

    # Add current question
    messages.append({
        "role":    "user",
        "content": question
    })

    # Step 5: Call Groq LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=500,
        temperature=0.3
    )

    return {
        "answer":  response.choices[0].message.content,
        "sources": [r["source"] for r in relevant],
        "score":   relevant[0]["similarity"]
    }


if __name__ == "__main__":
    test_questions = [
        "What are symptoms of malaria?",
        "What is HIV?",
        "How do I prevent cholera?",
        "What is trachoma?",
        "how do I repair a bicycle?",
    ]

    for q in test_questions:
        print(f"\n{'='*55}")
        print(f"Q: {q}")
        result = ask(q)
        print(f"Score:   {result['score']}")
        print(f"Sources: {result['sources']}")
        print(f"Answer:  {result['answer'][:250]}")


