# ai-pipeline/embeddings/db.py
import os
import sys
import psycopg2
from dotenv import load_dotenv

# --- PATH & MODULE RESOLUTION FIX ---
# Ensures the app finds the environment variables regardless of where it is executed from
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)   # Points to 'ai-pipeline'
project_root = os.path.dirname(parent_dir)  # Points to 'healthbridge-africa' workspace root

if os.path.exists(os.path.join(project_root, ".env")):
    load_dotenv(os.path.join(project_root, ".env"))
else:
    load_dotenv(os.path.join(parent_dir, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Get a raw connection to the PostgreSQL database."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is missing or empty!")
    return psycopg2.connect(DATABASE_URL)