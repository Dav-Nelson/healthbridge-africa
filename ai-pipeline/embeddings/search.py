from embeddings.db import get_connection
from embeddings.embed import get_embedding

KNOWN_DISEASES = {
    # English
    "malaria": "malaria",
    "hiv": "hiv",
    "aids": "hiv",
    "cholera": "cholera",
    "tuberculosis": "tuberculosis",
    "tb": "tuberculosis",
    "diarrhea": "diarrhea",
    "trachoma": "trachoma",
    "typhoid": "typhoid",
    "hypertension": "hypertension",
    "dengue": "dengue",

    # Amharic
    "ወባ": "malaria",
    "ኮሌራ": "cholera",
    "ሳንባ ነቀርሳ": "tuberculosis",
    "ኤችአይቪ": "hiv",

    # Afaan Oromo
    "busaa": "malaria",
    "koleeraa": "cholera",
    "tuberkuloosii": "tuberculosis",
    "hiv": "hiv",
    "aids": "aids",
    "tiraakoomaa": "trachoma",
    "dengue": "dengue",

    # Swahili
    "malaria": "malaria",
    "kipindupindu": "cholera",
    "tuberkulosi": "tuberculosis",
    "hiv": "hiv",
    "aids": "aids",
    "trachoma": "trachoma",
    "dengue": "dengue",
    

    # Hausa
    "zazzabin cizon sauro": "malaria",
    "cholera": "cholera",
    "tuberculosis": "tuberculosis",
    "hiv": "hiv",
    "aids": "aids",
    "trachoma": "trachoma",
    "dengue": "dengue",
    
}

def detect_condition(question: str):
    q = question.lower()
    for keyword, disease in KNOWN_DISEASES.items():
        if keyword.lower() in q:
            return disease
    return None


def search(question: str, top_k: int = 5) -> list:
    condition = detect_condition(question)
    print(f"🔍 Searching: {question}")
    print(f"   Detected condition: {condition}")

    question_embedding = get_embedding(question)

    # ✅ Force decimal notation — fixes scientific notation bug
    embedding_str = "[" + ",".join(
        f"{float(x):.8f}" for x in question_embedding
    ) + "]"

    conn = get_connection()
    cur = conn.cursor()

    # ✅ Fixed SQL — exactly 4 %s, exactly 4 values
    cur.execute("""
        SELECT
            source,
            content,
            country,
            condition,
            (
                1 - (embedding <=> %s::vector)
                +
                CASE
                    WHEN %s IS NOT NULL
                    AND LOWER(condition) LIKE '%%' || %s || '%%'
                    THEN 0.30
                    ELSE 0
                END
            ) AS similarity
        FROM health_documents
        ORDER BY similarity DESC
        LIMIT %s;
    """, (
        embedding_str,   # 1 → embedding <=>
        condition,       # 2 → WHEN %s IS NOT NULL
        condition,       # 3 → LIKE '%%' || %s || '%%'
        top_k            # 4 → LIMIT %s
    ))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"\nRAW RESULTS ({len(rows)} rows)")
    chunks = []
    for source, content, country, condition_name, similarity in rows:
        print(f"  [{float(similarity):.4f}] {source} — {condition_name}")
        chunks.append({
            "source":     source,
            "content":    content,
            "country":    country,
            "condition":  condition_name,
            "similarity": round(float(similarity), 4)
        })

    return chunks


if __name__ == "__main__":
    for q in ["What are symptoms of malaria?", "What is HIV?", "how to fix a bicycle?"]:
        print(f"\n{'='*50}")
        results = search(q, top_k=3)