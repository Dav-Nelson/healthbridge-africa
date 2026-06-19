"""
FastAPI server for HealthBridge Africa AI Pipeline.
Node.js backend calls these endpoints.

Run: uvicorn main:app --reload --port 8000
     (from inside ai-pipeline/ folder)
"""
import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

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


class QuestionRequest(BaseModel):
    question: str
    language: str = "en"
    history: List[dict] = []


class SpeakRequest(BaseModel):
    text: str
    language: str = "en"


def get_full_language_name(lang_code: str) -> str:
    return SUPPORTED_LANGUAGES.get(lang_code.lower(), "English")


def map_to_whisper_lang(lang_code: str) -> str:
    whisper_lang_map = {
        "en": "en",
        "sw": "sw",
        "am": "am",
        "om": "om",
        "pcm": "en",
        "tw": "en"
    }
    return whisper_lang_map.get(lang_code.lower(), "en")


@app.get("/")
def home():
    return {
        "message": "HealthBridge Africa AI Pipeline running",
        "version": "0.2.0",
        "endpoints": ["/ask", "/transcribe", "/speak"]
    }


@app.post("/ask")
async def ask_question(data: QuestionRequest):
    """Text question → grounded health answer via RAG + Groq (with history)."""
    from rag.query import ask_rag

    try:
        target_lang_name = get_full_language_name(data.language)
        result = ask_rag(data.question, language=target_lang_name, history=data.history)

        return {
            "question": data.question,
            "answer": result["answer"],
            "similarity_score": result["score"],
            "sources": result.get("sources", []),
            "language": data.language
        }
    except Exception as e:
        print(f"Error in /ask: {str(e)}")
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


@app.post("/speak")
async def speak(data: SpeakRequest):
    """Standalone Text-to-Speech Engine Endpoint."""
    from tts.speak import text_to_speech

    try:
        if not data.text:
            raise HTTPException(status_code=400, detail="Text payload parameter cannot be empty")

        audio_result = text_to_speech(data.text, data.language)

        if isinstance(audio_result, str) and audio_result.startswith("data:audio/"):
            raw_base64 = audio_result.split(",")[1] if "," in audio_result else audio_result
            return {
                "status": "success",
                "audio": raw_base64
            }

        raise HTTPException(
            status_code=500,
            detail="TTS engine did not return a valid audio payload."
        )

    except Exception as e:
        print(f"CRITICAL TTS /speak failure exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))