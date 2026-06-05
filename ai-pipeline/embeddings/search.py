from db import get_connection
from embed import get_embedding


def search(question, top_k=8):
    print(f"🔍 Searching for: {question}")

    # Create embedding for question
    question_embedding = get_embedding(question)

    # Convert embedding list into pgvector format
    question_embedding_str = "[" + ",".join(
        str(x) for x in question_embedding
    ) + "]"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            source,
            content,
            country,
            1 - (embedding <=> %s::vector) AS similarity
        FROM health_documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (
        question_embedding_str,
        question_embedding_str,
        top_k
    ))

    results = cur.fetchall()
    print("\nRAW RESULTS")

    # for row in results:
    #     print(row[0], row[3])
    for r in results:
        print(f"Source: {r[0]}, Similarity: {r[3]:.4f}")

    print(f"Rows returned: {len(results)}")

    cur.close()
    conn.close()

    chunks = []

    for source, content, country, similarity in results:

        # Ignore extremely weak matches
        # if similarity < 0.20:
        #     continue

        chunks.append({
            "source": source,
            "content": content,
            "country": country,
            "similarity": round(similarity, 4)
        })

    return chunks


if __name__ == "__main__":

    results = search(
        # "What are symptoms of malaria?",
        "What is HIV?",
        top_k=8
    )
