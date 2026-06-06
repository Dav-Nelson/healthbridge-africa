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
from pydantic import BaseModel
from dotenv import load_dotenv
from langdetect import detect
from openai import OpenAI

# ── Path setup ────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Groq client ───────────────────────────────────────────
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ── Import RAG ────────────────────────────────────────────
from embeddings.rag import ask as rag_ask
from embeddings.search import search
from tts.speak import text_to_speech

# ── Supported languages ───────────────────────────────────
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
    language: str = "en"

class SearchRequest(BaseModel):
    question: str


# ── Translation helpers ───────────────────────────────────

def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a medical translator for African languages. "
                    "Translate the following text to English accurately. "
                    "IMPORTANT: ወባ in Amharic means MALARIA not rabies. "
                    "Busaa in Oromo means MALARIA. "
                    "ነቀርሳ means TUBERCULOSIS. "
                    "ኮሌራ means CHOLERA. "
                    "Preserve all medical terms correctly. "
                    "Respond with ONLY the English translation, nothing else."
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()
    return response.choices[0].message.content.strip()


def translate_answer_back(answer: str, target_lang: str) -> str:
    """Translate English RAG answer back to user's language."""
    if target_lang == "en":
        return answer

    lang_name = SUPPORTED_LANGUAGES.get(target_lang, target_lang)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a health information translator. "
                    f"Translate the following English health text to {lang_name}. "
                    f"Keep medical terms accurate and simple. "
                    f"Keep the response easy to understand for community members. "
                    f"Respond with ONLY the translated text, nothing else."
                )
            },
            {"role": "user", "content": answer}
        ],
        temperature=0.1,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()


# ── Endpoints ─────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "HealthBridge Africa AI Pipeline running",
        "version": "0.3.0",
        "supported_languages": SUPPORTED_LANGUAGES,
        "endpoints": ["/ask", "/transcribe", "/voice-agent", "/search", "/embed"]
    }


@app.post("/ask")
async def ask_question(data: QuestionRequest):
    """
    Text question in any language → answer in same language.

    Flow:
      1. Translate question to English
      2. Search pgvector RAG (English)
      3. Generate grounded answer (English)
      4. Translate answer back to user's language
    """
    try:
        user_lang = data.language.lower().strip()
        print(f"\n📥 Question ({user_lang}): {data.question}")

        # Step 1: Translate to English
        english_question = translate_to_english(data.question, user_lang)
        print(f"🔤 English: {english_question}")

        # Step 2+3: RAG search + answer
        result = rag_ask(english_question)
        english_answer = result["answer"]
        print(f"💬 Answer (en): {english_answer[:100]}...")

        # Step 4: Translate back to user language
        final_answer = translate_answer_back(english_answer, user_lang)
        print(f"🌍 Answer ({user_lang}): {final_answer[:100]}...")

        return {
            "question":         data.question,
            "english_question": english_question,
            "answer":           final_answer,
            "language":         user_lang,
            "similarity_score": result.get("score", 0),
            "sources":          result.get("sources", []),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = None
):
    """Audio file → transcribed text using Groq Whisper (auto language detect)."""
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with open(temp_path, "rb") as audio_file:
            kwargs = dict(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json"
            )
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
    language: str = "en"
):
    """Audio → STT → Translate → RAG → Translate back → Answer"""
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: STT
        with open(temp_path, "rb") as audio_file:
            kwargs = dict(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json"
            )
            if language and language.lower() not in ("auto", "none", ""):
                kwargs["language"] = language

            transcription = client.audio.transcriptions.create(**kwargs)

        user_text         = transcription.text
        detected_language = getattr(transcription, "language", language)
        print(f"STT: {user_text} | Lang: {detected_language}")

        # Step 2: Translate to English
        english_question = translate_to_english(user_text, detected_language)

        # Step 3: RAG
        rag_result = rag_ask(english_question)

        # Step 4: Translate back
        final_answer = translate_answer_back(rag_result["answer"], detected_language)

        return {
            "detected_language": detected_language,
            "user_text":         user_text,
            "english_question":  english_question,
            "answer":            final_answer,
            "similarity_score":  rag_result.get("score", 0),
            "sources":           rag_result.get("sources", [])
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
    """Audio → STT → RAG → TTS → audio response"""
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json"
            )

        user_text = transcription.text
        english_question = translate_to_english(user_text, language)
        rag_result = rag_ask(english_question)
        final_answer = translate_answer_back(rag_result["answer"], language)
        audio_response = text_to_speech(final_answer, language)

        return {
            "user_text":  user_text,
            "answer":     final_answer,
            "audio_file": audio_response,
            "sources":    rag_result.get("sources", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/search")
async def search_endpoint(data: SearchRequest):
    """Semantic search — returns top 5 chunks from pgvector."""
    try:
        chunks = search(data.question, top_k=5)
        return {"question": data.question, "chunks": chunks}
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