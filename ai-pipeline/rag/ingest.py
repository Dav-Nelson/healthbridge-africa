# ai-pipeline/rag/ingest.py
"""
Chunks health documents, embeds each chunk using Groq's embedding
(via nomic-embed-text on Groq), and saves to vector_store.json

Run from repo root:
    python ai-pipeline/rag/ingest.py
"""
import os
import json
# from groq import Groq
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer

# load_dotenv(dotenv_path="ai-pipeline/.env")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list:
    """Get embedding using Groq's embedding endpoint."""
    # NOTE: Groq doesn't have embeddings yet — we use their HTTP API
    # For now we use the ollama embed locally just for ingest,
    # OR use a free HuggingFace embedding (no GPU needed)
    # Best free option: sentence-transformers (runs locally, no API needed)
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer("all-MiniLM-L6-v2")  # 80MB, free, fast

    return embed_model.encode(text).tolist()


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list:
    """Split text into overlapping word chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def ingest_file(filepath: str, source_name: str):
    """Read a document, chunk it, embed each chunk, save to vector store."""
    
    print(f"\nIngesting: {source_name}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        
    if not text.strip():
        print(f"Skipping empty file: {source_name}")
        return
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")
    
    vector_data = []
    
    for i, chunk in enumerate(chunks):
        print(f"  Embedding chunk {i+1}/{len(chunks)}...")
        
        embedding = get_embedding(chunk)   # ✅ embeds EACH chunk, not whole text
        
        vector_data.append({               # ✅ INSIDE the loop
            "source": source_name,
            "chunk_index": i,
            "text": chunk,                 # ✅ saves the chunk, not whole text
            "embedding": embedding
        })
    
    # Load existing store if it exists, then append
    store_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "vector_store.json"
    )
    store_path = os.path.abspath(store_path)
    existing = []
    if os.path.exists(store_path):
        with open(store_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    
    existing.extend(vector_data)
    
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False)
    
    print(f"✅ Stored {len(vector_data)} chunks from '{source_name}'")
    print(f"   Total chunks in store: {len(existing)}")


if __name__ == "__main__":
    # Ingest all your health documents
    store_path = "docs/vector_store.json"

    with open(store_path, "w", encoding="utf-8") as f:
        json.dump([], f)
        
    docs = [
        ("docs/malaria.txt", "Malaria Guidelines"),
        ("knowledge-base/ethiopia-health-facts.md", "Ethiopia Health Facts"),
        ("knowledge-base/ghana-health-facts.md", "Ghana Health Facts"),
        ("knowledge-base/kenya-health-facts.md", "Kenya Health Facts"),
        ("knowledge-base/nigeria-health-facts.md", "Nigeria Health Facts"),
        ("knowledge-base/WHO-guidelines.md", "WHO Guidelines"),
        ("knowledge-base/sources.md", "Sources")
    ]
    
    for filepath, source_name in docs:
        if os.path.exists(filepath):
            ingest_file(filepath, source_name)
        else:
            print(f"⚠️  Skipping (file not found): {filepath}")