"""
FastAPI server for HealthBridge Africa AI Pipeline.
Node.js backend calls these endpoints.

Run: uvicorn main:app --reload --port 8000
     (from inside ai-pipeline/ folder)
"""
import os
import sys
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

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
    language: str = "en"
    history: List[dict] = []  # Added for conversation memory


class SpeakRequest(BaseModel):
    """Added schema to parse plain-text parameters sent from the Express proxy routing layer."""
    text: str
    language: str = "en"


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
        "endpoints": ["/ask", "/transcribe", "/voice-agent", "/voice-chat", "/speak"]
    }


@app.post("/ask")
async def ask_question(data: QuestionRequest):
    """Text question → grounded health answer via RAG + Groq (with history)."""
    # Lazy import prevents heavy AI libraries from loading until actually needed
    from rag.query import ask_rag
    
    try:
        # Convert incoming lang code ("am", "pcm") into full name string
        target_lang_name = get_full_language_name(data.language)
        
        # Pass history to ask_rag
        result = ask_rag(data.question, language=target_lang_name, history=data.history)
        
        return {
            "question": data.question,
            "answer": result["answer"],
            "similarity_score": result["score"],
            "sources": result.get("sources", []),
            "language": data.language
        }
    except Exception as e:
        # Log the specific error for debugging
        print(f"Error in /ask: {str(e)}")
        # Raise an HTTP exception to notify the client
        raise HTTPException(status_code=500, detail="Error processing your health query.")


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
        
        # Step 2: RAG answer
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
    # Lazy imports: only load heavy AI modules when this endpoint is hit
    from rag.query import ask_rag
    from tts.speak import text_to_speech
    
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

        # Step 2: Grounded RAG Query Processing
        target_lang_name = get_full_language_name(language)
        rag_result = ask_rag(user_text, language=target_lang_name)

        # Step 3: Text-To-Speech Synthesis processing native response string
        audio_response = text_to_speech(rag_result["answer"], target_lang_name)

        raw_audio = audio_response.split(",")[1] if (isinstance(audio_response, str) and "data:audio/" in audio_response) else audio_response

        return {
            "user_text": user_text,
            "answer": rag_result["answer"],
            "audio_file": audio_response,
            "audio": raw_audio,
            "sources": rag_result.get("sources", [])
        }

    except Exception as e:
        print(f"Error in /voice-chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/speak")
async def speak(data: SpeakRequest):
    """
    Standalone Text-to-Speech Engine Endpoint.
    Delivers base64 or file data dynamically back to client architecture.
    """
    # Lazy import prevents heavy TTS library from loading until called
    from tts.speak import text_to_speech
    
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