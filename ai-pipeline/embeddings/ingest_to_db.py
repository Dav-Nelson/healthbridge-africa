import os
import glob
from db import get_connection
from chunker import chunk_text        # now returns list of dicts
from embed import get_embedding

def format_embedding(embedding: list) -> str:
    """Force decimal notation — never scientific notation like 1e-07"""
    return "[" + ",".join(f"{float(x):.8f}" for x in embedding) + "]"

def ingest_file(filepath: str, source_name: str, country: str):
    print(f"\n📄 Ingesting: {source_name}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    print(f"  📦 {len(chunks)} chunks created")

    conn = get_connection()
    cur = conn.cursor()

    # Clear old chunks for this source
    cur.execute("DELETE FROM health_documents WHERE source = %s", (source_name,))

    for i, chunk in enumerate(chunks):
        print(f"  🔢 Embedding chunk {i+1}/{len(chunks)} [{chunk['condition'][:40]}]...")

        embedding     = get_embedding(chunk["content"])
        embedding_str = format_embedding(embedding)    # ← fix scientific notation

        cur.execute("""
            INSERT INTO health_documents
                (source, country, condition, content, embedding)
            VALUES (%s, %s, %s, %s, %s::vector)
        """, (
            source_name,
            country,
            chunk["condition"],   # ← now stores section name
            chunk["content"],
            embedding_str
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ Stored {len(chunks)} chunks")


if __name__ == "__main__":
    docs = [
        ("knowledge-base/ethiopia-health-facts.md", "ethiopia-health-facts", "ethiopia"),
        ("knowledge-base/ghana-health-facts.md",    "ghana-health-facts",    "ghana"),
        ("knowledge-base/kenya-health-facts.md",    "kenya-health-facts",    "kenya"),
        ("knowledge-base/nigeria-health-facts.md",  "nigeria-health-facts",  "nigeria"),
        ("knowledge-base/WHO-guidelines.md",        "WHO-guidelines",        "global"),
    ]

    for filepath, source_name, country in docs:
        if os.path.exists(filepath):
            ingest_file(filepath, source_name, country)
        else:
            print(f"⚠️  Skipping (not found): {filepath}")