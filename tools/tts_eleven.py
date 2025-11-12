# tools/tts_eleven.py
import os, requests, json, time
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# voice map: ضع هنا أسماء الأصوات المتاحة في ElevenLabs إذا أردت أصوات مُحدّدة
VOICE_MAP = {
    "female":"alloy",
    "male":"adam"
}

def synthesize_eleven(text, voice="female", out_path="output.mp3"):
    # Simplified ElevenLabs TTS via API v1
    # Docs: https://api.elevenlabs.io (adjust if Eleven updated endpoints)
    if ELEVEN_API_KEY is None:
        raise RuntimeError("ELEVEN_API_KEY not set")
    voice_id = VOICE_MAP.get(voice, list(VOICE_MAP.values())[0])
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability":0.5,"similarity_boost":0.75}
    }
    r = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
    if r.status_code not in (200,201):
        raise RuntimeError(f"ElevenLabs TTS failed: {r.status_code} {r.text}")
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return out_path
