import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model locally
model = SentenceTransformer("all-MiniLM-L6-v2")

# Path to the JSON file created by ingest.py
STORE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs/vector_store.json"))

def search_documents(query: str, top_k: int = 3):
    if not os.path.exists(STORE_PATH):
        print(f"Error: Vector store not found at {STORE_PATH}")
        return []

    with open(STORE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert query to embedding
    query_emb = model.encode(query)

    # Calculate Cosine Similarity
    results = []
    for item in data:
        chunk_emb = np.array(item["embedding"])
        # Cosine similarity formula: (A . B) / (||A|| * ||B||)
        norm_a = np.linalg.norm(query_emb)
        norm_b = np.linalg.norm(chunk_emb)
        
        if norm_a == 0 or norm_b == 0:
            similarity = 0
        else:
            similarity = np.dot(query_emb, chunk_emb) / (norm_a * norm_b)
            
        results.append({
            "text": item["text"],
            "source": item["source"],
            "score": float(similarity)
        })

    # Sort by score descending and return top K
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]