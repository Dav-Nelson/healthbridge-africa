import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".env"
    )
)

HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_API_KEY
)


def get_embedding(text):

    embedding = client.feature_extraction(
        text,
        model="sentence-transformers/all-mpnet-base-v2"
    )

    # HuggingFace inference returns a NumPy array; convert to native Python list for psycopg2
    return embedding[:768].tolist()