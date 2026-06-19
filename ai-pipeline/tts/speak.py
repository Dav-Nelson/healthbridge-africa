# ai-pipeline/tts/speak.py
import base64
from io import BytesIO
from gtts import gTTS

def text_to_speech(text: str, language: str = "en") -> str:
    """
    Converts localized response text into an in-memory MP3 stream,
    encoding it as a Base64 data URI string to bypass disk write limitations.
    Dynamically routes regional accents (TLDs) for localized language trust.
    """
    gtts_lang_map = {
        "en": "en",
        "sw": "sw",
        "am": "am",
        "om": "om",
        "pcm": "en",
        "tw": "en"
    }

    gtts_tld_map = {
        "en": "com.ng",
        "pcm": "com.ng",
        "tw": "com.ng",
        "om": "co.za",
        "sw": "com",
        "am": "com"
    }

    target_gtts_code = gtts_lang_map.get(language.lower(), "en")
    target_tld = gtts_tld_map.get(language.lower(), "com.ng")

    try:
        mp3_fp = BytesIO()
        tts = gTTS(text=text, lang=target_gtts_code, tld=target_tld)
        tts.write_to_fp(mp3_fp)

        mp3_fp.seek(0)
        audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")

        return f"data:audio/mp3;base64,{audio_base64}"
    except Exception as e:
        print(f"TTS Engine Error: {str(e)}")
        try:
            mp3_fp = BytesIO()
            fallback_tts = gTTS(text="An audio processing error occurred.", lang="en", tld="com.ng")
            fallback_tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
            return f"data:audio/mp3;base64,{audio_base64}"
        except Exception:
            return ""