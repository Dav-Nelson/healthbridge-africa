# ai-pipeline/tts/speak.py

from gtts import gTTS
import uuid
import os


def text_to_speech(text: str, language: str = "en"):
    filename = f"audio_{uuid.uuid4().hex}.mp3"

    tts = gTTS(
        text=text,
        lang=language
    )

    tts.save(filename)

    return filename