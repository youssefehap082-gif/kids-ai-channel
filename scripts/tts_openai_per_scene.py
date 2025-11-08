#!/usr/bin/env python3
# scripts/tts_openai_per_scene.py
import os, json, time, subprocess
from pathlib import Path
from gtts import gTTS
import requests

OUT = Path("output")
OUT.mkdir(parents=True, exist_ok=True)
script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json - run generate_script_facts.py first")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])
OPENAI_KEY = os.environ.get("OPENAI_API_KEY","").strip()

def openai_tts_stream(text, outpath, voice="alloy"):
    # Use OpenAI TTS endpoint; may need model changes depending on API access.
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    payload = {"model":"gpt-4o-mini-tts","voice":voice,"input":text}
    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=120) as r:
            if r.status_code == 200:
                with open(outpath, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            fh.write(chunk)
                return True
            else:
                print("OpenAI TTS fail:", r.status_code, r.text[:200])
                return False
    except Exception as e:
        print("OpenAI TTS exception:", e)
        return False

for s in scenes:
    idx = s["idx"]
    text = s["text"]
    out_mp3 = OUT / f"scene_{idx}.mp3"
    print("Generating TTS for scene", idx)
    ok = False
    if OPENAI_KEY:
        voice = "alloy" if idx % 2 == 0 else "verse"
        for attempt in range(2):
            if openai_tts_stream(text, str(out_mp3), voice=voice):
                ok = True
                break
            time.sleep(1+attempt*2)
    if not ok:
        try:
            tts = gTTS(text, lang='en', slow=False)
            tts.save(str(out_mp3))
            ok = True
        except Exception as e:
            print("gTTS error:", e)
    if ok:
        print("Saved audio:", out_mp3.name)
    else:
        print("Failed audio for scene", idx)
    time.sleep(0.5)

# build narration_full.mp3 by concatenation (ffmpeg concat)
audio_files = [OUT / f"scene_{s['idx']}.mp3" for s in scenes if (OUT / f"scene_{s['idx']}.mp3").exists()]
if audio_files:
    listfile = OUT / "audio_list.txt"
    with open(listfile, "w", encoding="utf-8") as f:
        for a in audio_files:
            f.write(f"file '{a.resolve()}'\n")
    out_full = OUT / "narration_full.mp3"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listfile), "-c","copy", str(out_full)], check=False)
    print("Built narration_full.mp3")
else:
    print("No per-scene audio files found.")
