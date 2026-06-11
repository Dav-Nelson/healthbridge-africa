# embeddings/chunker.py
import re

def chunk_text(text: str, chunk_size: int = 500) -> list[dict]:
    """
    Section-aware chunker.
    Splits on ## headings first, then by word count within sections.
    Each chunk knows its source section (condition name).
    """
    chunks = []

    # Split document on ## headings (each disease section)
    sections = re.split(r'\n(?=## )', text)

    for section in sections:
        if not section.strip():
            continue

        # Extract section title (first line)
        lines = section.strip().split('\n')
        title = lines[0].replace('#', '').strip()

        words = section.split()

        # If section fits in one chunk — keep it whole
        if len(words) <= chunk_size:
            chunks.append({
                "content":   section.strip(),
                "condition": title,
            })
        else:
            # Split large sections into overlapping chunks
            overlap = 75
            i = 0
            part = 0
            while i < len(words):
                chunk_words = words[i: i + chunk_size]
                chunks.append({
                    "content":   " ".join(chunk_words),
                    "condition": title,
                })
                i += chunk_size - overlap
                part += 1

    return chunks


if __name__ == "__main__":
    with open("../knowledge-base/ethiopia-health-facts.md", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")
    for i, c in enumerate(chunks):
        print(f"\nChunk {i+1} | Section: {c['condition']}")
        print(f"Words: {len(c['content'].split())}")
        print(f"Preview: {c['content'][:120]}...")