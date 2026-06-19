# ai-pipeline/embeddings/embed.py
import os
import sys
import cohere
from dotenv import load_dotenv

# --- PATH & MODULE RESOLUTION FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)   # Points to 'ai-pipeline'
project_root = os.path.dirname(parent_dir)  # Points to workspace root

if os.path.exists(os.path.join(project_root, ".env")):
    load_dotenv(os.path.join(project_root, ".env"))
else:
    load_dotenv(os.path.join(parent_dir, ".env"))

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def get_embedding(text: str) -> list:
    """Embed using Cohere."""
    if not text.strip():
        return []
    
    response = co.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_query"
    )
    return response.embeddings[0]