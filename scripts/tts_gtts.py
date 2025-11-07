# scripts/tts_gtts.py
import os, json, time
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

for s in scenes:
    idx = s.get("idx")
    text = s.get("text","").strip()
    if not text:
        continue
    fn = OUT / f"scene{idx}.mp3"
    try:
        tts = gTTS(text, lang='en', slow=False)
        tts.save(str(fn))
        print("Saved TTS", fn)
        time.sleep(0.6)
    except Exception as e:
        print("gTTS error for scene", idx, e)
