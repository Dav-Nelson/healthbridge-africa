"""
FastAPI server for HealthBridge Africa AI Pipeline.
Node.js backend calls these endpoints.

Run: uvicorn api.main:app --reload --port 8000
     (from inside ai-pipeline/ folder)
"""
import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # Added for streaming generated audio files
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# ── SYSTEM PATH CORRECTION ──────────────────────────────
# Force Python to read the parent directories so modules like api, tts, and embeddings resolve cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from langdetect import detect
from tts.speak import text_to_speech
from openai import OpenAI

from api.memory import (
    get_history, 
    add_message
)

from embeddings.rag import ask
load_dotenv(dotenv_path=os.path.join(parent_dir, ".env"))

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
SUPPORTED_LANGUAGES = {
    "en":  "English",
    "am":  "Amharic",
    "om":  "Afaan Oromoo",
    "sw":  "Swahili",
    "pcm": "Nigerian Pidgin",
    "tw":  "Twi",
    "ha":  "Hausa",
    "fr":  "French",
}

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


app = FastAPI(
    title="HealthBridge Africa — AI Pipeline",
    description="Multilingual voice health agent for Africa",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ────────────────────────────────────────
class QuestionRequest(BaseModel):
    question: str
    language: str = "auto"
    session_id: str = None  # Optional session ID for conversation history tracking

class SpeakRequest(BaseModel):
    """Added schema to parse plain-text parameters sent from the Express proxy routing layer."""
    text: str
    language: str = "en"

# ── Endpoints ─────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "HealthBridge Africa AI Pipeline running",
        "version": "0.3.0",
        "endpoints": ["/ask", "/transcribe", "/voice-agent", "/voice-chat", "/speak", "/health"]
    }


# ── RENDER HEALTH CHECK ENDPOINT ──────────────────────────
@app.get("/health")
@app.head("/health")
def health_check():
    """Render health check endpoint to prevent deployment loop timeouts."""
    return {"status": "healthy", "database": "connected"}


@app.post("/ask")
async def ask_question(data: QuestionRequest):
    """
    Text question in any language → answer in same language.
    """
    try:
            history = get_history(data.session_id)

            result = ask(
                question=data.question,
                history=history
            )

            add_message(
                data.session_id,
                "user",
                data.question
            )

            add_message(
                data.session_id,
                "assistant",
                result["answer"]
            )
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
    language: str = "en"
):
    """
    Audio file → transcribed text using Groq Whisper.
    """
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Transcribe with Groq Whisper (cloud, free tier)
        with open(temp_path, "rb") as audio_file:
            kwargs = {
                "model": "whisper-large-v3",
                "file": audio_file,
                "response_format": "verbose_json"
            }

            if language and language.lower() not in ("auto", "none", ""):
                kwargs["language"] = language

            transcription = client.audio.transcriptions.create(**kwargs)
        
        return {
            "text":              transcription.text,
            "detected_language": getattr(transcription, "language", "unknown"),
            "status":            "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/voice-agent")
async def voice_agent(
    file: UploadFile = File(...),
    language: str = None  # Auto-detect language from audio for more natural user experience
):
    """
    Full pipeline: Audio → STT → RAG → Answer
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

        user_text = transcription.text

        try:
            detected_language = detect(user_text)
        except:
            detected_language = language

        print(f"STT result: {user_text}")
        print(f"Detected language: {detected_language}")
        
        # Step 2: RAG answer (Groq Llama 3)
        rag_result = ask(user_text)        
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

        user_text = (
            transcription.get("text", "")
            if isinstance(transcription, dict)
            else transcription.text
        )
        # RAG
        rag_result = ask(user_text)
        

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
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            

@app.post("/speak")
async def speak(data: SpeakRequest):
    """
    Standalone Text-to-Speech Engine Endpoint.
    """
    try:
        if not data.text:
            raise HTTPException(status_code=400, detail="Text payload parameter cannot be empty")
            
        target_lang_name = get_full_language_name(data.language)
        
        audio_result = text_to_speech(data.text, target_lang_name)
        
        if isinstance(audio_result, str) and audio_result.startswith("data:audio/"):
            raw_base64 = audio_result.split(",")[1] if "," in audio_result else audio_result
            return {
                "status": "success",
                "audio": raw_base64
            }
            
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        static_dir = os.path.join(base_dir, "static")
        
        file_path = os.path.join(static_dir, str(audio_result))
        if not os.path.exists(file_path):
            file_path = os.path.join(base_dir, str(audio_result))
        if not os.path.exists(file_path):
            file_path = os.path.abspath(str(audio_result))
            
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/mpeg", filename=str(audio_result))
            
        raise HTTPException(
            status_code=404, 
            detail=f"Audio pipeline asset resolution mismatch. File not found on disk context path: {audio_result}"
        )
        
    except Exception as e:
        print(f"CRITICAL TTS /speak failure exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))