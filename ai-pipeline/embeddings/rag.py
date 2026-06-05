from groq import Groq
from dotenv import load_dotenv
import os

from search import search

load_dotenv(
    os.path.join(os.path.dirname(__file__), "..", ".env")
)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# question = "What are symptoms of hiv?"
question = "how do I repair a bicycle?"

# Retrieve relevant chunks
results = search(question, top_k=8)

# Build context
context = "\n\n".join(
    [r["content"] for r in results]
)

# Build prompt
prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}
"""


response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    # model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": (
                "You are HealthBridge Africa's health information assistant. "
                "Use ONLY the supplied context. "
                "Never diagnose diseases. "
                "Never prescribe medication. "
                "Never invent information. "
                "If the answer is not in the context, say so clearly."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
)
if len(results) == 0:
    print("No relevant information found.")
    exit()
else:
    print("\nANSWER:\n")
    print(response.choices[0].message.content)

# print(prompt)
