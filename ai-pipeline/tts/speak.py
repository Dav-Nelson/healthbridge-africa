# ai-pipeline/tts/speak.py
import os
import uuid
from gtts import gTTS

def text_to_speech(text: str, language: str = "en") -> str:
    """
    Converts localized response text into an audio file safely.
    Protects the app from crashing on unsupported languages like Pidgin or Twi.
    """
    # 1. Cleanly resolve paths to save audio inside a dedicated temp/ or public/ directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.abspath(os.path.join(base_dir, "..", "static", "audio"))
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    full_file_path = os.path.join(output_dir, filename)

    # 2. Map frontend lang codes to valid gTTS language identifiers
    # gTTS natively supports: 'en' (English), 'sw' (Swahili), 'am' (Amharic)
    gtts_lang_map = {
        "en": "en",
        "sw": "sw",
        "am": "am",
        "om": "en",   # Fallback Oromo audio narration to English if dialect support fluctuates
        "pcm": "en",  # gTTS lacks native Pidgin—fallback to English text reading to avoid app crashes
        "tw": "en"    # gTTS lacks native Twi—fallback to English text reading to avoid app crashes
    }
    
    target_gtts_code = gtts_lang_map.get(language.lower(), "en")

    try:
        # 3. Instantiate gTTS safely
        tts = gTTS(
            text=text,
            lang=target_gtts_code
        )
        tts.save(full_file_path)
        
        # Return the absolute or relative file path to the server endpoint
        return full_file_path

    except Exception as e:
        print(f"TTS Engine Error: {str(e)}")
        # Ultimate fallback baseline to guarantee an audio file object is returned
        fallback_tts = gTTS(text="An audio processing error occurred.", lang="en")
        fallback_tts.save(full_file_path)
        return full_file_path