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
    # 1. Map frontend lang codes to valid gTTS language identifiers
    gtts_lang_map = {
        "en": "en",
        "sw": "sw",
        "am": "am",
        "om": "en",   # Fallback if dialect support fluctuates
        "pcm": "en",  # Fallback Pidgin audio narration to English text reader
        "tw": "en"    # Fallback Twi audio narration to English text reader
    }
    
    # 2. Dynamic Top Level Domain (tld) localization to match regional accents
    # 'com.ng' provides a natural West African English voice context
    gtts_tld_map = {
        "en": "com.ng",
        "pcm": "com.ng",
        "tw": "com.ng",
        "om": "com.ng",
        "sw": "com",  # Native Swahili handles its own localization perfectly under 'com'
        "am": "com"   # Native Amharic handles its own localization perfectly under 'com'
    }
    
    target_gtts_code = gtts_lang_map.get(language.lower(), "en")
    target_tld = gtts_tld_map.get(language.lower(), "com.ng")

    try:
        # 3. Write the audio directly into a memory buffer instead of disk
        mp3_fp = BytesIO()
        tts = gTTS(text=text, lang=target_gtts_code, tld=target_tld)
        tts.write_to_fp(mp3_fp)
        
        # 4. Rewind buffer stream pointer and convert binary data to Base64
        mp3_fp.seek(0)
        audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
        
        # 5. Return standard web format Base64 Data URI
        return f"data:audio/mp3;base64,{audio_base64}"

    except Exception as e:
        print(f"TTS Engine Error: {str(e)}")
        # Ultimate baseline fallback in memory with clean West African English voice configuration
        try:
            mp3_fp = BytesIO()
            fallback_tts = gTTS(text="An audio processing error occurred.", lang="en", tld="com.ng")
            fallback_tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
            return f"data:audio/mp3;base64,{audio_base64}"
        except Exception:
            return ""