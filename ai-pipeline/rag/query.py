import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="ai-pipeline/.env")

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------------------------------------------------------
# Vector Store Import
# ---------------------------------------------------------

try:
    from rag.vector_store import search_documents
except ImportError:
    try:
        from vector_store import search_documents
    except ImportError:
        search_documents = None


# ---------------------------------------------------------
# Translation Helper
# ---------------------------------------------------------

def translate_to_english(text: str) -> str:
    """
    Translate multilingual user queries into English
    for semantic search.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a medical translator for African languages.

IMPORTANT HEALTH TERMS:
- ወባ = Malaria
- Busaa = Malaria
- ነቀርሳ = Tuberculosis
- ኮሌራ = Cholera
- HIV = HIV
- AIDS = AIDS

Rules:
1. Translate ONLY into English.
2. Do NOT explain.
3. Do NOT answer.
4. Do NOT add extra words.
5. If already English, return unchanged.
6. Return only the translated sentence.
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0,
            max_tokens=100
        )

        translated = response.choices[0].message.content.strip()

        if translated:
            return translated

        return text

    except Exception as e:
        print(f"[Translation Error] {e}")
        return text


# ---------------------------------------------------------
# Fallback Knowledge Base
# ---------------------------------------------------------

FALLBACK_CONTEXT = """
Malaria is a mosquito-borne disease caused by parasites.
Common symptoms include fever, chills, headache, fatigue,
and body aches. Severe malaria can be life-threatening.
People with symptoms should seek medical attention promptly.
"""


# ---------------------------------------------------------
# Main RAG Function
# ---------------------------------------------------------

def ask_rag(question: str, language: str = "English") -> dict:

    print(f"\n[RAG] Incoming Question: {question}")
    print(f"[RAG] Target Language: {language}")

    # -----------------------------------------------------
    # Step 1: Translate for Retrieval
    # -----------------------------------------------------

    search_query = translate_to_english(question)

    print(f"[RAG] Search Query: {search_query}")

    # -----------------------------------------------------
    # Step 2: Vector Search
    # -----------------------------------------------------

    top_chunks = []

    if search_documents is not None:

        try:
            top_chunks = search_documents(
                search_query,
                top_k=3
            )
            
            print("\n===== TOP CHUNKS =====")

            for i, chunk in enumerate(top_chunks):
                print(
                    f"{i+1}. score={chunk['score']:.4f} "
                    f"source={chunk['source']}"
                )

            print("======================\n")


            print(
                f"[RAG] Retrieved {len(top_chunks)} chunks"
            )

        except Exception as e:
            print(f"[Vector Search Error] {e}")

    else:
        print(
            "[WARNING] search_documents import failed."
        )

    # -----------------------------------------------------
    # Step 3: Fallback
    # -----------------------------------------------------

    if not top_chunks:

        top_chunks = [{
            "text": FALLBACK_CONTEXT,
            "score": 0.50,
            "source": "Fallback Knowledge Base"
        }]

    best_score = top_chunks[0]["score"]

    # -----------------------------------------------------
    # Step 4: Confidence Check
    # -----------------------------------------------------

    if best_score < 0.40:

        return {
            "answer": (
                "I could not find reliable information "
                "in the HealthBridge knowledge base. "
                "Please consult a qualified healthcare professional."
            ),
            "context": "",
            "score": round(best_score, 4),
            "sources": []
        }

    # -----------------------------------------------------
    # Step 5: Build Context
    # -----------------------------------------------------

    context_parts = []

    for chunk in top_chunks:

        source = chunk.get(
            "source",
            "HealthBridge Knowledge Base"
        )

        text = chunk.get(
            "text",
            ""
        )

        context_parts.append(
            f"[Source: {source}]\n{text}"
        )

    context = "\n\n".join(context_parts)
    context = context[:6000]

    # -----------------------------------------------------
    # Step 6: Generate Answer
    # -----------------------------------------------------

    system_prompt = f"""
You are HealthBridge Africa's health assistant.

IMPORTANT:
- Respond entirely in {language}.
- Use ONLY the provided context.
- Never invent facts.
- Never diagnose disease.
- Never prescribe medication.
- If information is unavailable, say so.
- Recommend professional medical care for severe symptoms.
- Keep language simple and easy to understand.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content":
                        f"Context:\n{context}\n\n"
                        f"Question:\n{question}"
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content

    except Exception as e:

        print(f"[Generation Error] {e}")

        answer = (
            "Sorry, I encountered an error while "
            "generating a response."
        )

    # -----------------------------------------------------
    # Step 7: Return
    # -----------------------------------------------------

    return {
        "answer": answer,
        "context": context,
        "score": round(best_score, 4),
        "sources": list(
            set(
                chunk.get("source", "unknown")
                for chunk in top_chunks
            )
        )
    }