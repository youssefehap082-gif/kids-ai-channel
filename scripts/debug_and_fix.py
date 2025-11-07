#!/usr/bin/env python3
# scripts/debug_and_fix.py
# Diagnostic + auto-fix orchestrator:
# 1) print env & folders
# 2) if output has mp4 -> report success and exit 0
# 3) run generate_videos.py (full pipeline)
# 4) re-check output; if still empty -> run fallback generator
# 5) finally: attempt upload (if YouTube secrets present) by calling upload_youtube.py

import os, sys, time, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
OUT = ROOT / "output"
CLIPS = ROOT / "clips"
TH = ROOT / "thumbnails"
MUSIC = ROOT / "assets" / "music"
STATE = ROOT / "state"

def println(*a, **k):
    print(*a, **k, flush=True)

def check_env():
    keys = ["PEXELS_API_KEY","OPENAI_API_KEY","PIXABAY_API_KEY","REPLICATE_API_TOKEN","HF_API_TOKEN",
            "YT_CLIENT_ID","YT_CLIENT_SECRET","YT_REFRESH_TOKEN","YT_CHANNEL_ID"]
    println("=== ENVIRONMENT SECRETS ===")
    miss = []
    for k in keys:
        v = os.environ.get(k)
        println(f"{k}: {'SET' if v else 'MISSING'}")
        if not v:
            miss.append(k)
    return miss

def list_dirs():
    println("\n=== FILESYSTEM QUICK VIEW ===")
    for d in [ROOT, CLIPS, OUT, TH, MUSIC, STATE]:
        try:
            println(f"{d}: exists={d.exists()} files={len(list(d.glob('*'))) if d.exists() else 0}")
            if d.exists():
                for f in sorted(list(d.glob("*")))[:20]:
                    println("  -", f.name, "-", f.stat().st_size, "bytes")
        except Exception as e:
            println("  (err listing)", e)

def find_output_mp4s():
    if not OUT.exists():
        return []
    return sorted([p for p in OUT.glob("*.mp4")])

def run_cmd(cmd, env=None, check=True):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    println("\n>>> CMD:", " ".join(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=merged, text=True)
    for line in p.stdout:
        println(line.rstrip())
    p.wait()
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed {p.returncode}: {' '.join(cmd)}")
    return p.returncode

def try_pipeline():
    # Prefer to run generate_videos.py if present
    gv = SCRIPTS / "generate_videos.py"
    if gv.exists():
        println("\n=== Running generate_videos.py (full pipeline) ===")
        try:
            run_cmd(["python3", str(gv)])
        except Exception as e:
            println("[PIPELINE] generate_videos.py failed:", e)
    else:
        # fallback: try known build scripts in order
        println("generate_videos.py not found; trying build_info_video.py and build_ambient_videos.py sequentially")
        for name in ["build_info_video.py","build_ambient_videos.py"]:
            p = SCRIPTS / name
            if p.exists():
                try:
                    run_cmd(["python3", str(p)])
                except Exception as e:
                    println(f"[PIPELINE] {name} failed:", e)
            else:
                println(f"[PIPELINE] {name} not present; skipping.")

def run_fallback():
    fb = SCRIPTS / "generate_fallback_videos.py"
    if fb.exists():
        println("\n=== Running fallback generator ===")
        try:
            run_cmd(["python3", str(fb)])
        except Exception as e:
            println("[FALLBACK] generate_fallback_videos.py failed:", e)
    else:
        println("[FALLBACK] No generate_fallback_videos.py found in scripts/")

def attempt_upload():
    # call upload_youtube.py output if YT secrets present
    required = ["YT_CLIENT_ID","YT_CLIENT_SECRET","YT_REFRESH_TOKEN","YT_CHANNEL_ID"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        println("\n=== UPLOAD SKIPPED: Missing YouTube secrets:", missing)
        println("If you want auto-upload, add YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CHANNEL_ID as repo secrets.")
        return
    uploader = SCRIPTS / "upload_youtube.py"
    if not uploader.exists():
        println("[UPLOAD] upload_youtube.py not found in scripts/ — cannot upload automatically.")
        return
    println("\n=== Attempting upload_youtube.py output ===")
    try:
        run_cmd(["python3", str(uploader), str(OUT)])
    except Exception as e:
        println("[UPLOAD] upload_youtube.py failed:", e)

def main():
    println("DEBUG & FIX START —", time.asctime())
    miss = check_env()
    list_dirs()
    mp4s = find_output_mp4s()
    if mp4s:
        println("\nFOUND mp4 files in output/:")
        for p in mp4s:
            println(" -", p.name, p.stat().st_size, "bytes")
        println("\nNo further action required by debug script. If you want re-upload, uploader can be called now.")
        attempt_upload()
        return
    println("\nNo mp4 found in output/. Will run full pipeline now (generate_videos.py or builds).")
    try:
        try_pipeline()
    except Exception as e:
        println("[ERROR] Pipeline execution error:", e)

    time.sleep(1)
    mp4s = find_output_mp4s()
    if mp4s:
        println("\nSUCCESS: After pipeline, found mp4 files:")
        for p in mp4s:
            println(" -", p.name, p.stat().st_size)
        attempt_upload()
        return

    println("\nPipeline did NOT produce output mp4 files. Attempting fallback generator to ensure upload has files.")
    run_fallback()

    time.sleep(1)
    mp4s = find_output_mp4s()
    if mp4s:
        println("\nSUCCESS: After fallback, found mp4 files:")
        for p in mp4s:
            println(" -", p.name, p.stat().st_size)
        attempt_upload()
        return

    println("\nFAILED: No mp4 files produced even after fallback. Please send full Action log to me.")
    list_dirs()
    println("DEBUG & FIX END —", time.asctime())
    sys.exit(2)

if __name__ == "__main__":
    main()
