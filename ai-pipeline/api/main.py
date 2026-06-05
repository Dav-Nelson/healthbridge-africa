# ai-pipeline/main.py
"""
FastAPI server for HealthBridge Africa AI Pipeline.
Node.js backend calls these endpoints.

Run: uvicorn main:app --reload --port 8000
     (from inside ai-pipeline/ folder)
"""
import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

from langdetect import detect
from tts.speak import text_to_speech
from openai import OpenAI

from embeddings.rag import ask as rag_ask
from embeddings.search import search

# Make sure rag/ is importable
# sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rag.query import ask_rag

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "am": "Amharic",
    "sw": "Swahili",
    "om": "Oromo",
    "pcm": "Nigerian Pidgin",
    "tw": "Twi"
}
app = FastAPI(
    title="HealthBridge Africa — AI Pipeline",
    description="Multilingual voice health agent for Africa",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ───────────────────────────────────────
class QuestionRequest(BaseModel):
    question: str
    language: str = "auto"


# ── Endpoints ────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "HealthBridge Africa AI Pipeline running",
        "version": "0.2.0",
        "endpoints": ["/ask", "/transcribe", "/voice-agent"]
    }


@app.post("/ask")
async def ask_question(data: QuestionRequest):
    """Text question → grounded health answer via RAG + Groq."""
    try:
        result = ask_rag(data.question)
        return {
            "question": data.question,
            "answer": result["answer"],
            "similarity_score": result["score"],
            "sources": result.get("sources", []),
            "language": data.language
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base not ready. Run ingest.py first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = None
):
    """
    Audio file → transcribed text using Groq Whisper.
    
    language options: "en", "sw", "om", "ha" (Hausa), etc.
    Pass from frontend based on user's selected language.
    """
    temp_path = f"temp_{file.filename}"
    
    try:
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Transcribe with Groq Whisper (cloud, free tier)
        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",   # Best Whisper model, free on Groq
                file=audio_file,
                # language=language,           # Forced language — no guessing
                response_format="verbose_json"
            )
        
        return {
            "text": transcription.text,
            "detected_language": transcription.language,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Always clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/voice-agent")
async def voice_agent(
    file: UploadFile = File(...),
    language: str = "auto"
):
    """
    Full pipeline: Audio → STT → RAG → Answer
    This is the main endpoint the voice UI will use.
    
    Returns: what the user said + health answer
    """
    temp_path = f"temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Step 1: Speech to Text (Groq Whisper)
        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=language,
                response_format="json"
            )
        
        # user_text = transcription.text
        # print(f"STT result: {user_text}")
        
        user_text = transcription.text

        try:
            detected_language = detect(user_text)
        except:
            detected_language = language

        print(f"STT result: {user_text}")
        print(f"Detected language: {detected_language}")
        
        # Step 2: RAG answer (Groq Llama 3)
        rag_result = ask_rag(user_text)
        
        return {
            "detected_language": detected_language,
            "user_text": user_text,
            "answer": rag_result["answer"],
            "similarity_score": rag_result["score"],
            "sources": rag_result.get("sources", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
@app.post("/voice-chat")
async def voice_chat(
    file: UploadFile = File(...),
    language: str = "en"
):
    temp_path = f"temp_{file.filename}"

    try:

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # STT
        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=language,
                response_format="json"
            )

        user_text = transcription.text

        # RAG
        rag_result = ask_rag(user_text)

        # TTS
        audio_response = text_to_speech(
            rag_result["answer"],
            language
        )

        return {
            "user_text": user_text,
            "answer": rag_result["answer"],
            "audio_file": audio_response,
            "sources": rag_result.get("sources", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    

class SearchRequest(BaseModel):
    question: str

@app.post("/search")
async def search_endpoint(data: SearchRequest):
    """Semantic search — returns top 3 chunks from pgvector."""
    try:
        chunks = search(data.question, top_k=3)
        return {
            "question": data.question,
            "chunks":   chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed")
async def embed_endpoint(data: SearchRequest):
    """Full RAG — search pgvector + Groq Llama answer."""
    try:
        result = rag_ask(data.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))