import cohere
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def get_embedding(text: str) -> list:
    """
    Embed using Cohere.
    Free: 1000 requests/month.
    Returns 1024-dimensional vector.
    """
    response = co.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_document"
    )
    return response.embeddings[0]


if __name__ == "__main__":
    vec = get_embedding("What are symptoms of malaria?")
    print(f"✅ Dimensions: {len(vec)}")   # 1024
    print(f"   First 5:    {vec[:5]}")