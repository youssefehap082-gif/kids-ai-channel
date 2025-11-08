#!/usr/bin/env python3
# scripts/generate_one_video.py
import os, time, subprocess
from pathlib import Path

SCRIPTS = Path(__file__).parent
ROOT = SCRIPTS.parent
OUT = ROOT / "output"

def run(cmd, env=None):
    print(">>>", " ".join(cmd))
    merged = os.environ.copy()
    if env:
        merged.update(env)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=merged, text=True)
    for line in p.stdout:
        print(line.rstrip())
    p.wait()
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

def ensure_dirs():
    for d in ["output","clips","state","thumbnails","assets/music"]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

def attempt_upload():
    required = ["YT_CLIENT_ID","YT_CLIENT_SECRET","YT_REFRESH_TOKEN","YT_CHANNEL_ID"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print("[UPLOAD] Missing YT secrets, skipping upload:", missing)
        return
    run(["python3", str(SCRIPTS / "upload_youtube.py"), str(OUT)])

def build_info_once():
    run(["python3", str(SCRIPTS / "generate_script_facts.py")])
    run(["python3", str(SCRIPTS / "tts_openai_per_scene.py")])
    run(["python3", str(SCRIPTS / "download_and_prepare_clips.py")])
    run(["python3", str(SCRIPTS / "build_info_video.py")])
    run(["python3", str(SCRIPTS / "generate_thumbnail.py")])

def build_ambient_once():
    # For ambient: reuse same script generation or a simpler ambient builder you have
    run(["python3", str(SCRIPTS / "generate_script_facts.py")])
    run(["python3", str(SCRIPTS / "download_and_prepare_clips.py")])
    run(["python3", str(SCRIPTS / "build_ambient_videos.py")])
    run(["python3", str(SCRIPTS / "generate_thumbnail.py")])

def main():
    ensure_dirs()
    mode = os.environ.get("MODE","info").lower()
    print("MODE:", mode)
    try:
        if mode == "ambient":
            build_ambient_once()
        else:
            build_info_once()
    except Exception as e:
        print("[ERROR] build failed:", e)
        # fallback: generate simple color fallback files so uploader has something
        if (SCRIPTS / "generate_fallback_videos.py").exists():
            print("[INFO] Running fallback generator...")
            run(["python3", str(SCRIPTS / "generate_fallback_videos.py")])
    # finally attempt upload if configured
    attempt_upload()
    print("DONE at", time.asctime())

if __name__ == "__main__":
    main()
