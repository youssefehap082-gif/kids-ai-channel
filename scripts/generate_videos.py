#!/usr/bin/env python3
# scripts/generate_videos.py  (updated to call fallback if no outputs)
import os, sys, subprocess, time, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
OUT = ROOT / "output"

def run(cmd, env=None, check=True):
    print(">>> RUN:", " ".join(cmd))
    merged = os.environ.copy()
    if env:
        merged.update(env)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=merged, text=True)
    for line in p.stdout:
        print(line.rstrip())
    p.wait()
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(cmd)}")
    return p.returncode

def ensure_dirs():
    for d in ["output","clips","state","thumbnails","assets/music"]:
        Path(d).mkdir(parents=True, exist_ok=True)

def run_full_pipeline():
    ensure_dirs()
    # Attempt: 3 info + 2 ambient as before
    for i in range(1,4):
        print("\n=== INFO RUN", i, "===\n")
        run(["python3", str(SCRIPTS / "generate_script_animal.py")])
        run(["python3", str(SCRIPTS / "download_stock_videos.py")])
        run(["python3", str(SCRIPTS / "music_fetcher.py")])
        run(["python3", str(SCRIPTS / "tts_service.py")])
        env = os.environ.copy(); env["MODE"]="info"
        run(["python3", str(SCRIPTS / "build_single_video.py")], env=env)
        run(["python3", str(SCRIPTS / "generate_thumbnail.py")])
        time.sleep(1)
    for j in range(1,3):
        print("\n=== AMBIENT RUN", j, "===\n")
        run(["python3", str(SCRIPTS / "generate_script_animal.py")])
        run(["python3", str(SCRIPTS / "download_stock_videos.py")])
        run(["python3", str(SCRIPTS / "music_fetcher.py")])
        env = os.environ.copy(); env["MODE"]="ambient"
        run(["python3", str(SCRIPTS / "build_single_video.py")], env=env)
        run(["python3", str(SCRIPTS / "generate_thumbnail.py")])
        time.sleep(1)

def count_output_videos():
    if not OUT.exists():
        return 0
    mp4s = list(OUT.glob("*.mp4"))
    return len(mp4s)

def call_fallback():
    print("No video files found — creating fallback videos now...")
    run(["python3", str(SCRIPTS / "generate_fallback_videos.py")])
    print("Fallback generation finished.")

def try_upload():
    # if YouTube secrets present, attempt upload
    missing = [k for k in ("YT_CLIENT_ID","YT_CLIENT_SECRET","YT_REFRESH_TOKEN","YT_CHANNEL_ID") if not os.environ.get(k)]
    if missing:
        print("YouTube secrets missing, skipping upload. Missing:", missing)
        return
    print("Calling uploader...")
    run(["python3", str(SCRIPTS / "upload_youtube.py"), str(OUT)])

def main():
    try:
        run_full_pipeline()
    except Exception as e:
        print("Pipeline error:", e)
    # check output
    n = count_output_videos()
    print("Output mp4 count:", n)
    if n == 0:
        call_fallback()
    else:
        print("Found output videos, will proceed to upload if configured.")
    # final check / manifest
    try_upload()
    print("Done orchestration.")

if __name__ == "__main__":
    main()
