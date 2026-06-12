import os
from pydoc import text

from chunker import chunk_text

KNOWLEDGE_BASE = "knowledge-base"


def load_documents():

    documents = []

    for file in os.listdir(KNOWLEDGE_BASE):

        if file.endswith(".md"):

            path = os.path.join(
                KNOWLEDGE_BASE,
                file
            )

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                text = f.read()

            documents.append({
                "source": file,
                "content": text
            })

    return documents


def prepare_chunks():

    docs = load_documents()

    all_chunks = []

    for doc in docs:
        
        print(doc["source"])
        print("character:", len(doc["content"]))
        print("words:", len(doc["content"].split()))

        chunks = chunk_text(doc["content"])

        print(f"{doc['source']} -> {len(chunks)} chunks")

        for chunk in chunks:

            # country = doc["source"].split("-")[0]
            filename = doc["source"].lower()

            if filename.startswith("ethiopia"):
                country = "ethiopia"
            elif filename.startswith("ghana"):
                country = "ghana"
            elif filename.startswith("kenya"):
                country = "kenya"
            elif filename.startswith("nigeria"):
                country = "nigeria"
            else:
                country = "general"

            all_chunks.append({
                "source": doc["source"],
                "chunk": chunk,
                "country": country
            })

    print(f"\nTOTAL CHUNKS: {len(all_chunks)}")

    return all_chunks


if __name__ == "__main__":

    chunks = prepare_chunks()

    print(
        f"Total chunks: {len(chunks)}"
        f" | Sample chunk source: {chunks[2]['source']}"
    )
    print(len(chunks))

    # print("\nSample:\n")

    # print(chunks[0]["chunk"][:500])