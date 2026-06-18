import os
import time
import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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


def get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list:
    """Generate a normalized 768-dim embedding via Gemini API."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=768
        )
    )
    vector = result.embeddings[0].values

    norm = sum(v * v for v in vector) ** 0.5
    normalized = [v / norm for v in vector] if norm > 0 else vector
    return normalized


def ingest_file_to_db(filepath, source_name, cur):
    print(f"Ingesting {source_name} into DB...")
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk, task_type="RETRIEVAL_DOCUMENT")
        cur.execute(
            "INSERT INTO knowledge_base (source_name, chunk_index, text, embedding) VALUES (%s, %s, %s, %s)",
            (source_name, i, chunk, embedding)
        )
        time.sleep(0.5)
    print(f"✅ Stored {len(chunks)} chunks.")


def main():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    docs = [
        ("ai-pipeline/knowledge-base/ethiopia-health-facts.md", "Ethiopia Health Facts"),
        ("ai-pipeline/knowledge-base/ghana-health-facts.md", "Ghana Health Facts"),
        ("ai-pipeline/knowledge-base/kenya-health-facts.md", "Kenya Health Facts"),
        ("ai-pipeline/knowledge-base/nigeria-health-facts.md", "Nigeria Health Facts"),
        ("ai-pipeline/knowledge-base/WHO-guidelines.md", "WHO Guidelines"),
    ]

    for path, name in docs:
        ingest_file_to_db(path, name, cur)
        conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()