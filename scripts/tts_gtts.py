# scripts/tts_gtts.py
import json, time, os
from gtts import gTTS
from pathlib import Path
OUT = Path("output")
OUT.mkdir(parents=True, exist_ok=True)

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])

# create one narration by concatenating scene texts with small breaks
texts = []
for s in scenes:
    texts.append(s.get("text",""))
    texts.append(" ")  # small pause
full_text = " .  ".join(texts).strip()

# fallback minimal
if not full_text:
    full_text = "Learn about this animal. Subscribe for more fun facts!"

outp = OUT / "narration.mp3"
try:
    tts = gTTS(full_text, lang='en', slow=False)
    tts.save(str(outp))
    print("Saved narration", outp)
except Exception as e:
    print("gTTS error:", e)
    # If fails, create silent file
    open(outp, "wb").close()
    print("Created empty narration file as fallback.")
time.sleep(1)
