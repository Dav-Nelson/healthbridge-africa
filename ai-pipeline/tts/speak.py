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
            text=text,# ai-pipeline/tts/speak.py
import base64
from io import BytesIO
from gtts import gTTS

def text_to_speech(text: str, language: str = "en") -> str:
    """
    Converts localized response text into an in-memory MP3 stream,
    encoding it as a Base64 data URI string to bypass disk write limitations.
    """
    # 1. Map frontend lang codes to valid gTTS language identifiers
    gtts_lang_map = {
        "en": "en",
        "sw": "sw",
        "am": "am",
        "om": "en",   # Fallback if dialect support fluctuates
        "pcm": "en",  # Fallback Pidgin audio narration to English text reader
        "tw": "en"    # Fallback Twi audio narration to English text reader
    }
    
    target_gtts_code = gtts_lang_map.get(language.lower(), "en")

    try:
        # 2. Write the audio directly into a memory buffer instead of disk
        mp3_fp = BytesIO()
        tts = gTTS(text=text, lang=target_gtts_code)
        tts.write_to_fp(mp3_fp)
        
        # 3. Rewind buffer stream pointer and convert binary data to Base64
        mp3_fp.seek(0)
        audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
        
        # 4. Return standard web format Base64 Data URI
        return f"data:audio/mp3;base64,{audio_base64}"

    except Exception as e:
        print(f"TTS Engine Error: {str(e)}")
        # Ultimate baseline fallback in memory
        try:
            mp3_fp = BytesIO()
            fallback_tts = gTTS(text="An audio processing error occurred.", lang="en")
            fallback_tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
            return f"data:audio/mp3;base64,{audio_base64}"
        except Exception:
            return ""
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