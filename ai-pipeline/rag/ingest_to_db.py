import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv(dotenv_path="ai-pipeline/.env")

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

embed_model = SentenceTransformer("all-MiniLM-L6-v2")


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


def ingest_file_to_db(filepath, source_name):
    print(f"Ingesting {source_name} into DB...")
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = embed_model.encode(chunk).tolist()
        cur.execute(
            "INSERT INTO knowledge_base (source_name, chunk_index, text, embedding) VALUES (%s, %s, %s, %s)",
            (source_name, i, chunk, embedding)
        )
    conn.commit()
    print(f"✅ Stored {len(chunks)} chunks.")


if __name__ == "__main__":
    docs = [
        ("ai-pipeline/knowledge-base/ethiopia-health-facts.md", "Ethiopia Health Facts"),
        ("ai-pipeline/knowledge-base/ghana-health-facts.md", "Ghana Health Facts"),
        ("ai-pipeline/knowledge-base/kenya-health-facts.md", "Kenya Health Facts"),
        ("ai-pipeline/knowledge-base/nigeria-health-facts.md", "Nigeria Health Facts"),
        ("ai-pipeline/knowledge-base/WHO-guidelines.md", "WHO Guidelines"),
    ]

    for path, name in docs:
        ingest_file_to_db(path, name)

    cur.close()
    conn.close()