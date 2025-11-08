#!/usr/bin/env python3
# scripts/generate_one_video.py
import os, time, subprocess
from pathlib import Path

SCRIPTS = Path(__file__).parent
ROOT = SCRIPTS.parent
OUT = ROOT / "output"

def run(cmd):
    print(">>>", cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        print(line.rstrip())
    p.wait()
    if p.returncode != 0:
        raise RuntimeError("Command failed: " + cmd)

def ensure_dirs():
    for d in ["output","clips","state","thumbnails","assets/music"]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

def main():
    ensure_dirs()
    mode = os.environ.get("MODE","info")
    print("MODE:", mode)
    # 1) script
    run("python3 scripts/generate_script_facts.py")
    # 2) TTS
    run("python3 scripts/tts_openai_per_scene.py")
    # 3) download clips (Pexels then Pixabay) until MIN_DURATION or narration
    run("python3 scripts/download_and_prepare_clips.py")
    # 4) build final video
    run("python3 scripts/build_info_video.py")
    # 5) thumbnail
    run("python3 scripts/generate_thumbnail.py")
    # 6) upload (if YT secrets exist)
    try:
        run("python3 scripts/upload_youtube.py")
    except Exception as e:
        print("Upload step failed or skipped:", e)
    print("DONE run at", time.asctime())

if __name__ == "__main__":
    main()
