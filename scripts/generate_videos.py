#!/usr/bin/env python3
# scripts/generate_videos.py
# Orchestrator: generates 3 info videos + 2 ambient videos per run,
# by calling the repo scripts in order. Outputs go to output/.
#
# Usage (in runner): python3 scripts/generate_videos.py
# It expects the other scripts in scripts/:
# - generate_script_animal.py
# - download_stock_videos.py
# - music_fetcher.py
# - tts_service.py
# - build_single_video.py
# - generate_thumbnail.py
# - upload_youtube.py  (optional: will be called at end if YT secrets present)
#
# Make sure secrets env are set in GitHub Actions (PEXELS_API_KEY, OPENAI_API_KEY optional,
# YT_CLIENT_*, etc). This script prints logs to stdout so you can debug in Actions UI.

import os
import sys
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"

def run(cmd, env=None, check=True):
    """Run command and stream output. Raises on error if check=True."""
    print(">>> RUN:", " ".join(cmd))
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=merged_env, text=True)
    for line in p.stdout:
        print(line.rstrip())
    p.wait()
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(cmd)}")
    return p.returncode

def ensure_folders():
    for d in ["output", "clips", "state", "thumbnails", "assets/music"]:
        p = ROOT / d
        p.mkdir(parents=True, exist_ok=True)

def build_one_info(instance_idx):
    print("\n=== START INFO VIDEO #", instance_idx, "===")
    # 1) generate script (will write output/script.json and update state)
    run(["python3", str(SCRIPTS / "generate_script_animal.py")])
    # 2) download clips for that script
    run(["python3", str(SCRIPTS / "download_stock_videos.py")])
    # 3) fetch music (optional) so ambient videos can use it later
    #    safe to run every time
    run(["python3", str(SCRIPTS / "music_fetcher.py")])
    # 4) generate narration (OpenAI TTS preferred, fallback to gTTS)
    run(["python3", str(SCRIPTS / "tts_service.py")])
    # 5) build the video in info mode
    env = os.environ.copy()
    env["MODE"] = "info"
    run(["python3", str(SCRIPTS / "build_single_video.py")], env=env)
    # 6) thumbnail
    run(["python3", str(SCRIPTS / "generate_thumbnail.py")])
    print("=== DONE INFO VIDEO #", instance_idx, "===\n")
    time.sleep(2)  # small delay to be polite to APIs / runner

def build_one_ambient(instance_idx, minutes=7):
    print("\n=== START AMBIENT VIDEO #", instance_idx, "===")
    # 1) generate script for a new animal (so ambient has different visuals)
    run(["python3", str(SCRIPTS / "generate_script_animal.py")])
    # 2) download clips for that script
    run(["python3", str(SCRIPTS / "download_stock_videos.py")])
    # 3) fetch music (ensures assets/music populated)
    run(["python3", str(SCRIPTS / "music_fetcher.py")])
    # 4) build ambient video (MODE=ambient)
    env = os.environ.copy()
    env["MODE"] = "ambient"
    # you can control ambient length by editing build_single_video.py default target_minutes
    run(["python3", str(SCRIPTS / "build_single_video.py")], env=env)
    # 5) thumbnail
    run(["python3", str(SCRIPTS / "generate_thumbnail.py")])
    print("=== DONE AMBIENT VIDEO #", instance_idx, "===\n")
    time.sleep(2)

def upload_all_if_possible():
    # try to call upload_youtube.py output, but only if YT env vars are set
    missing = []
    for k in ("YT_CLIENT_ID","YT_CLIENT_SECRET","YT_REFRESH_TOKEN","YT_CHANNEL_ID"):
        if not os.environ.get(k):
            missing.append(k)
    if missing:
        print("[UPLOAD] YouTube secrets missing, skipping upload. Missing:", missing)
        return
    try:
        print("[UPLOAD] Starting upload to YouTube (output/).")
        run(["python3", str(SCRIPTS / "upload_youtube.py"), str(OUTPUT)])
        print("[UPLOAD] Upload step finished.")
    except Exception as e:
        print("[UPLOAD] Upload failed:", e)

def list_output_files():
    print("\n--- OUTPUT FOLDER CONTENT ---")
    if not OUTPUT.exists():
        print("output/ not found")
        return
    for p in sorted(OUTPUT.glob("*")):
        print(p.name, "-", p.stat().st_size, "bytes")
    mf = OUTPUT / ".build_manifest.json"
    if mf.exists():
        try:
            import json
            print("\nmanifest:", json.load(open(mf, encoding="utf-8")))
        except Exception:
            pass
    print("--- end output ---\n")

def main():
    try:
        ensure_folders()
        # Build 3 info videos
        for i in range(1, 4):
            build_one_info(i)
        # Build 2 ambient videos
        for j in range(1, 3):
            build_one_ambient(j)
        # summarize outputs
        list_output_files()
        # try upload
        upload_all_if_possible()
        print("\nALL DONE. If upload skipped, check YouTube secrets and run upload manually.")
    except Exception as e:
        print("\n[ERROR] Orchestration failed:", e)
        list_output_files()
        sys.exit(1)

if __name__ == "__main__":
    main()
