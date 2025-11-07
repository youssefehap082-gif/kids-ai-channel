#!/usr/bin/env python3
# scripts/generate_videos.py
import os, time, subprocess
from pathlib import Path
S = Path(__file__).parent
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
def main():
    # 3 info videos
    for i in range(3):
        run(["python3", str(S / "generate_script_facts.py")])
        run(["python3", str(S / "tts_openai_per_scene.py")])
        run(["python3", str(S / "download_and_prepare_clips.py")])
        run(["python3", str(S / "build_info_video.py")])
        run(["python3", str(S / "generate_thumbnail.py")])
        time.sleep(1)
    # 2 ambient videos
    run(["python3", str(S / "music_fetcher.py")])  # attempt to fetch music
    run(["python3", str(S / "download_and_prepare_clips.py")])  # fill clips for ambient
    run(["python3", str(S / "build_ambient_videos.py")])
    run(["python3", str(S / "generate_thumbnail.py")])
    # attempt upload if secrets present
    if os.environ.get("YT_CLIENT_ID") and os.environ.get("YT_CLIENT_SECRET") and os.environ.get("YT_REFRESH_TOKEN") and os.environ.get("YT_CHANNEL_ID"):
        run(["python3", str(S / "upload_youtube.py"), "output"])
    else:
        print("YouTube secrets missing - skipping upload.")
if __name__ == "__main__":
    main()
