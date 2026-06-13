"""
Chunks health documents, embeds each chunk using sentence-transformers,
and saves to vector_store.json

Run from repo root:
    python ai-pipeline/rag/ingest.py
"""
import os
import json
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv(dotenv_path="ai-pipeline/.env")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list:
    """Get embedding using local sentence-transformers model."""
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

def ingest_file(filepath: str, source_name: str, store_path: str):
    """Read a document, chunk it, embed each chunk, save to vector store."""
    print(f"\nIngesting: {source_name}")
    
    if not os.path.exists(filepath):
        print(f"⚠️  Skipping (file not found): {filepath}")
        return

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
        embedding = get_embedding(chunk)
        vector_data.append({
            "source": source_name,
            "chunk_index": i,
            "text": chunk,
            "embedding": embedding
        })
    
    existing = []
    if os.path.exists(store_path):
        with open(store_path, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
    
    existing.extend(vector_data)
    
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False)
    
    print(f"✅ Stored {len(vector_data)} chunks from '{source_name}'")

if __name__ == "__main__":
    # Ensure the docs directory exists
    store_path = os.path.abspath("ai-pipeline/docs/vector_store.json")
    os.makedirs(os.path.dirname(store_path), exist_ok=True)

    # Reset/Create empty store
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump([], f)
        
    docs = [
        ("ai-pipeline/knowledge-base/ethiopia-health-facts.md", "Ethiopia Health Facts"),
        ("ai-pipeline/knowledge-base/ghana-health-facts.md", "Ghana Health Facts"),
        ("ai-pipeline/knowledge-base/kenya-health-facts.md", "Kenya Health Facts"),
        ("ai-pipeline/knowledge-base/nigeria-health-facts.md", "Nigeria Health Facts"),
        ("ai-pipeline/knowledge-base/WHO-guidelines.md", "WHO Guidelines"),
        ("ai-pipeline/knowledge-base/sources.md", "Sources")
    ]
    
    for filepath, source_name in docs:
        ingest_file(filepath, source_name, store_path)
    
    print(f"\n✅ Ingestion complete. Total records in store.")