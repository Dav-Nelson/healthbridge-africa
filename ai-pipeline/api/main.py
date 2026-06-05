# ai-pipeline/api/main.py
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
from openai import OpenAI
from dotenv import load_dotenv

# Make sure rag/ is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rag.query import ask_rag
from tts.speak import text_to_speech

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Using OpenAI SDK interface wrapped around ultra-fast Groq endpoints
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Human-readable mapping to guide our custom Llama 3 RAG system prompt instruction
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
    language: str = "en"  # Standard default representation code


# ── Helper Language Routing Utilities ───────────────────
def get_full_language_name(lang_code: str) -> str:
    """Maps ISO code snippet prefixes to full descriptive names for Llama 3 prompt ingestion."""
    return SUPPORTED_LANGUAGES.get(lang_code.lower(), "English")


def map_to_whisper_lang(lang_code: str) -> str:
    """
    Safeguards Groq Whisper API from crashing when receiving non-ISO codes.
    Maps localized dialects to standard Whisper accepted tracking keys.
    """
    whisper_lang_map = {
        "en": "en",
        "sw": "sw",
        "am": "am",
        "om": "om",   # Whisper large-v3 supports Oromo natively
        "pcm": "en",  # Fallback Pidgin audio capture to English context for stabilization
        "tw": "en"    # Fallback Twi audio processing to English background engine
    }
    return whisper_lang_map.get(lang_code.lower(), "en")


# ── Endpoints ────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "HealthBridge Africa AI Pipeline running",
        "version": "0.2.0",
        "endpoints": ["/ask", "/transcribe", "/voice-agent", "/voice-chat"]
    }


@app.post("/ask")
async def ask_question(data: QuestionRequest):
    """Text question → grounded health answer via RAG + Groq."""
    try:
        # Convert incoming lang code ("am", "pcm") into full name string ("Amharic", "Nigerian Pidgin")
        target_lang_name = get_full_language_name(data.language)
        
        result = ask_rag(data.question, language=target_lang_name)
        return {
            "question": data.question,
            "answer": result["answer"],
            "similarity_score": result["score"],
            "sources": result.get("sources", []),
            "language": data.language
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base not ready. Run ingest.py first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "en"
):
    """Audio file → transcribed text using Groq Whisper with standard code protection."""
    temp_path = f"temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        target_whisper_code = map_to_whisper_lang(language)
        
        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=target_whisper_code,
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
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/voice-agent")
async def voice_agent(
    file: UploadFile = File(...),
    language: str = "en"
):
    """Full pipeline: Audio → STT → RAG → Multilingual Translated Text Answer"""
    temp_path = f"temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Protect transcription layer from unmapped language codes
        target_whisper_code = map_to_whisper_lang(language)
        
        # Step 1: Speech to Text (Groq Whisper)
        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=target_whisper_code,
                response_format="json"
            )
        
        user_text = transcription.get("text", "") if isinstance(transcription, dict) else transcription.text
        print(f"STT result: {user_text} | Target Language Prompt: {language}")
        
        # Step 2: RAG answer - Convert 'am'/'pcm' code to 'Amharic'/'Nigerian Pidgin' string
        target_lang_name = get_full_language_name(language)
        rag_result = ask_rag(user_text, language=target_lang_name)
        
        return {
            "detected_language": language, 
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
    """Complete End-To-End Loop: Audio Input → STT → RAG Engine → Audio Output Synthesis"""
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Speech to Text Transcription
        target_whisper_code = map_to_whisper_lang(language)
        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=target_whisper_code,
                response_format="json"
            )

        user_text = transcription.get("text", "") if isinstance(transcription, dict) else transcription.text

        # Step 2: Grounded RAG Query Processing passing explicit language formatting instructions
        target_lang_name = get_full_language_name(language)
        rag_result = ask_rag(user_text, language=target_lang_name)

        # Step 3: Text-To-Speech Synthesis processing native response string
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
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)