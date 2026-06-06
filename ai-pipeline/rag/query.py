def ask_rag(question: str, language: str = "English") -> dict:
    """Full RAG: search knowledge base, then answer with Groq Llama 3 in the target language."""
    
    # --- CROSS-LINGUAL ALIGNMENT FIX ---
    # If the question isn't in English, get a quick English translation for vector mapping
    search_query = question
    if language.lower() != "english":
        try:
            translation_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional medical translator. Translate the user query strictly into English. Return ONLY the plain English translation, nothing else."
                    },
                    {"role": "user", "content": question}
                ],
                max_tokens=100,
                temperature=0.0
            )
            search_query = translation_response.choices[0].message.content.strip()
            # Optional tracking log for your backend logs:
            print(f"[RAG Translation Log] Original: '{question}' -> Search Term: '{search_query}'")
        except Exception as e:
            print(f"Translation preprocessing failed: {e}")
            search_query = question # Fallback to original if API error
    # ------------------------------------

    # Now we pass the English search_query to hit your English markdown data chunks perfectly
    top_chunks = search_documents(search_query, top_k=3)
    
    if not top_chunks:
        return {
            "answer": "I don't have verified information on that. Please consult a healthcare provider.",
            "context": "",
            "score": 0,
            "sources": []
        }
        
    best_score = top_chunks[0]["score"]

    if best_score < 0.45:
        return {
            "answer": (
                "I could not find reliable information in the "
                "HealthBridge knowledge base for that question. "
                "Please consult a healthcare professional."
            ),
            "context": "",
            "score": round(best_score, 4),
            "sources": []
        }
    
    context_parts = []
    for chunk in top_chunks:
        context_parts.append(
            f"[Source: {chunk.get('source', 'Health Document')}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)
    context = context[:6000]
    
    # Dynamic language mapping to guide Llama 3 precisely
    system_instruction = (
        f"You are HealthBridge Africa's health information assistant.\n"
        f"CRITICAL: You MUST respond entirely in the following language/dialect: {language}.\n"
        f"Translate the health insights accurately into the tone and style of {language} while keeping the medical facts identical.\n"
        f"Use ONLY the supplied context. Never diagnose diseases. Never prescribe medication. "
        f"Never invent medical information. If the answer is not in the context, say so clearly. "
        f"Always recommend professional medical care when symptoms are severe or persistent. "
        f"Keep responses simple and easy to understand."
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                # Pass the original user question so it responds directly to their dialect input context
                "content": f"Context:\n{context}\n\nQuestion: {question}" 
            }
        ],
        max_tokens=500,
        temperature=0.3  
    )
    
    return {
        "answer": response.choices[0].message.content,
        "context": context,
        "score": round(top_chunks[0]["score"], 4),
        "sources": list(set([c.get("source", "unknown") for c in top_chunks]))
    }

if __name__ == "__main__":
    result = ask_rag("What are the symptoms of malaria and when should I see a doctor?")
    print("\n=== HealthBridge Africa Answer ===")
    print(result["answer"])
    print(f"\nTop similarity score: {result['score']}")
    print(f"Sources used: {result['sources']}")