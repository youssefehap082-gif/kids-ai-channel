# src/tts_utils.py
import os
import requests
from gtts import gTTS
from pathlib import Path

def generate_tts(text, out_path="voice.mp3", gender="female"):
    """
    Generate TTS audio.
    If ELEVEN_API_KEY + ELEVEN_VOICE_IDS provided in secrets, use ElevenLabs (preferred).
    Otherwise fallback to gTTS (works but single voice).
    Environment variables to optionally set:
      - ELEVEN_API_KEY
      - ELEVEN_VOICE_MALE (voice id)
      - ELEVEN_VOICE_FEMALE (voice id)
    """
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    if ELEVEN_API_KEY:
        # user must provide specific voice ids in secrets
        voice_id_key = "ELEVEN_VOICE_MALE" if gender == "male" else "ELEVEN_VOICE_FEMALE"
        voice_id = os.getenv(voice_id_key)
        if not voice_id:
            print(f"⚠️ ElevenLabs key present but {voice_id_key} not set — falling back to gTTS.")
        else:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": ELEVEN_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {"text": text}
            try:
                print("🔊 Using ElevenLabs TTS...")
                r = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
                r.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return out_path
            except Exception as e:
                print(f"⚠️ ElevenLabs TTS failed: {e}. Falling back to gTTS.")

    # Fallback to gTTS
    print("🔊 Using gTTS fallback...")
    tts = gTTS(text=text, lang="en", slow=False)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    tts.save(out_path)
    return out_path
