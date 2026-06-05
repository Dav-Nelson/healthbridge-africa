import os
import psycopg2
from dotenv import load_dotenv

# load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
  return psycopg2.connect(DATABASE_URL)

