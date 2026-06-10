import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def search_documents(query: str, top_k: int = 3):
    """
    Search vector_store.json using cosine similarity.
    """

    store_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "vector_store.json"
    )

    store_path = os.path.abspath(store_path)

    if not os.path.exists(store_path):
        return []

    with open(store_path, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    query_embedding = model.encode(query).tolist()

    scored = []

    for item in vectors:
        score = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        scored.append({
            "text": item["text"],
            "source": item["source"],
            "score": float(score)
        })

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored[:top_k]