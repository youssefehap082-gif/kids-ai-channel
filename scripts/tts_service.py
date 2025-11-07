# scripts/tts_service.py
import os, json, time, requests
from pathlib import Path
from gtts import gTTS

OUT = Path("output")
STATE = Path("state/state.json")

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])

# Build narration text
texts = []
for s in scenes:
    texts.append(s.get("headline",""))
    texts.append(s.get("text",""))
    texts.append(" ")
full_text = " .  ".join(texts).strip()
if not full_text:
    full_text = "Learn about this animal. Subscribe for more facts!"

OPENAI_KEY = os.environ.get("OPENAI_API_KEY","").strip()
outp = OUT / "narration.mp3"

# Determine voice gender to alternate
state = {}
if STATE.exists():
    try:
        state = json.load(open(STATE, encoding="utf-8"))
    except:
        state = {}
last_voice = state.get("last_voice","female")
# alternate
voice_gender = "male" if last_voice=="female" else "female"
state["last_voice"] = voice_gender
open(STATE, "w", encoding="utf-8").write(json.dumps(state, ensure_ascii=False, indent=2))
print("Selected voice gender:", voice_gender)

# Try OpenAI TTS if key present
if OPENAI_KEY:
    try:
        print("Trying OpenAI TTS...")
        # Try the OpenAI audio speech endpoint. This may require model name 'gpt-4o-mini-tts' or similar.
        # We'll attempt a request and write streamed response.
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
        # choose a voice name depending on gender - these names may vary by availability; fallback handled
        voice_name = "alloy" if voice_gender=="male" else "verse"
        payload = {
            "model": "gpt-4o-mini-tts",
            "voice": voice_name,
            "input": full_text
        }
        resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
        if resp.status_code == 200:
            with open(outp, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("Saved narration via OpenAI TTS:", outp)
            raise SystemExit(0)
        else:
            print("OpenAI TTS failed:", resp.status_code, resp.text[:300])
    except Exception as e:
        print("OpenAI TTS error:", e)

# Fallback to gTTS
try:
    print("Using gTTS fallback...")
    tts = gTTS(full_text, lang='en', slow=False)
    tts.save(str(outp))
    print("Saved narration via gTTS:", outp)
except Exception as e:
    print("gTTS error:", e)
    open(outp, "wb").close()
    print("Created empty narration file as fallback.")
time.sleep(0.5)
