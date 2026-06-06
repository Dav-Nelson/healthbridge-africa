import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Ensure environment variables are loaded securely
load_dotenv()

# Initialize the Groq client context explicitly inside this module
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# --- Keep your existing dependencies or placeholder functions ---
# Make sure search_documents is imported or accessible within your project structure
# from rag.vector_store import search_documents 

def ask_rag(question: str, language: str = "English") -> dict:
    """Full RAG: search knowledge base, then answer with Groq Llama 3 in the target language."""
    
    # --- STABILIZED CROSS-LINGUAL ALIGNMENT FIX ---
    # To protect against raw dialect lookups failing semantic score floors,
    # we dynamically extract an English equivalent search term using Groq.
    search_query = question
    try:
        translation_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional medical translator. Translate the user query strictly into English. If the query is already in English, return it exactly as it is. Return ONLY the plain English translation, nothing else."
                },
                {"role": "user", "content": question}
            ],
            max_tokens=100,
            temperature=0.0
        )
        translated_text = translation_response.choices[0].message.content.strip()
        if translated_text:
            search_query = translated_text
        print(f"[RAG Translation Log] Input: '{question}' -> Unified Search Term: '{search_query}'")
    except Exception as e:
        print(f"Translation preprocessing routing failed: {e}")
        search_query = question # Fallback baseline
    # ------------------------------------

    # Query your English vector-store using the cleanly aligned search term
    top_chunks = search_documents(search_query, top_k=3)
    
    # Structural fallback protection to prevent downstream 500 compilation crashes
    if not top_chunks:
        return {
            "answer": "I don't have verified information on that in the local database. Please consult a healthcare provider.",
            "context": "",
            "score": 0,
            "sources": []
        }
        
    best_score = top_chunks[0]["score"]

    if best_score < 0.45:
        return {
            "answer": (
                f"I could not find sufficiently reliable information in the "
                f"HealthBridge knowledge base regarding your question. "
                f"Please consult a professional medical healthcare worker."
            ),
            "context": "",
            "score": round(best_score, 4),
            "sources": []
        }
    
    context_parts = []
    for chunk in top_chunks:
        context_parts.append(
            f"[Source: {chunk.get('source', 'Health Document')}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)
    context = context[:6000]
    
    # Dynamic language instructions guiding Llama 3 generation properties
    system_instruction = (
        f"You are HealthBridge Africa's health information assistant.\n"
        f"CRITICAL: You MUST respond entirely in the following language/dialect: {language}.\n"
        f"Translate the health insights accurately into the tone and style of {language} while keeping the medical facts identical.\n"
        f"Use ONLY the supplied context. Never diagnose diseases. Never prescribe medication. "
        f"Never invent medical information. If the answer is not in the context, say so clearly. "
        f"Always recommend professional medical care when symptoms are severe or persistent. "
        f"Keep responses simple and easy to understand."
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}" 
            }
        ],
        max_tokens=500,
        temperature=0.3  
    )
    
    return {
        "answer": response.choices[0].message.content,
        "context": context,
        "score": round(top_chunks[0]["score"], 4),
        "sources": list(set([c.get("source", "unknown") for c in top_chunks]))
    }