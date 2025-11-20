import os
from gtts import gTTS

def generate_audio(script_data):
    # === FIX: Ensure temp directory exists ===
    os.makedirs("data/temp", exist_ok=True)
    # =========================================

    # Logic: ElevenLabs -> OpenAI -> gTTS
    audio_files = []
    for i, segment in enumerate(script_data['segments']):
        text = segment['text']
        filename = f"data/temp/audio_{i}.mp3"
        
        # Fallback chain
        if not _elevenlabs_tts(text, filename):
            if not _openai_tts(text, filename):
                _gtts_fallback(text, filename)
        
        audio_files.append(filename)
    return audio_files

def _elevenlabs_tts(text, filename):
    # Mock ElevenLabs call - returns False to trigger fallback in this demo
    return False

def _openai_tts(text, filename):
    # Mock OpenAI call
    return False

def _gtts_fallback(text, filename):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        return True
    except Exception as e:
        print(f"gTTS Failed: {e}")
        return False