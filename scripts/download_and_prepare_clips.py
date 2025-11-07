#!/usr/bin/env python3
# scripts/download_and_prepare_clips.py
# For each scene, query Pexels, pick a video, download and make sure its duration >= audio duration (trim/loop)
import os, json, time, math, random
import requests
from pathlib import Path
import subprocess, shlex

OUT = Path("output")
CLIPS = Path("clips")
CLIPS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY","").strip()
if not PEXELS_KEY:
    print("Set PEXELS_API_KEY in secrets.")
    raise SystemExit(1)

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json - generate script first.")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])

def get_audio_duration(fp):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(fp)])
        return float(out.strip())
    except:
        return None

def download_url(url, dest):
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(8192):
                if chunk:
                    fh.write(chunk)
    return True

search_url = "https://api.pexels.com/videos/search"
headers = {"Authorization": PEXELS_KEY}

for s in scenes:
    idx = s["idx"]
    query = s.get("query","animal")
    audio_file = OUT / f"scene_{idx}.mp3"
    adur = get_audio_duration(audio_file) or 6.0  # fallback small duration
    target = max(3.0, adur)  # seconds needed for scene
    print(f"[SCENE {idx}] query='{query}' audio={adur}s target={target}s")
    params = {"query": query, "per_page": 15, "size": "medium"}
    found = False
    try:
        r = requests.get(search_url, headers=headers, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            videos = data.get("videos", [])
            # prefer a video with duration >= target
            chosen = None
            for v in videos:
                if v.get("duration",0) >= target:
                    # prefer mp4 file with quality hd/sd
                    for vf in v.get("video_files",[]):
                        if vf.get("file_type")=="video/mp4":
                            chosen = vf
                            break
                    if chosen:
                        break
            # if none long enough pick best available
            if not chosen and videos:
                v = videos[0]
                chosen = v.get("video_files",[{}])[0]
            if chosen:
                url = chosen.get("link") or chosen.get("file_link") or chosen.get("url")
                dest = CLIPS / f"scene_{idx}_raw.mp4"
                print("Downloading clip for scene", idx, "from", url)
                try:
                    download_url(url, dest)
                    found = True
                except Exception as e:
                    print("Download error:", e)
    except Exception as e:
        print("Pexels API error:", e)
    # if not found, we'll create fallback single-color clip later (handled upstream)
    if not found:
        print(f"[WARN] No clip downloaded for scene {idx}. Scene will be skipped or fallback will be used.")
        continue
    # process: ensure clip length >= target by looping or trimming
    raw = CLIPS / f"scene_{idx}_raw.mp4"
    proc = CLIPS / f"scene_{idx}.mp4"
    vdur = None
    try:
        vdur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(raw)]).strip())
    except:
        vdur = None
    if vdur and vdur >= target - 0.1:
        # trim to exact target
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(raw), "-t", str(target), "-vf","scale=1280:720,setsar=1","-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(proc)], check=True)
    elif vdur and vdur > 0:
        # loop to reach target
        loops = math.ceil(target / vdur)
        listfile = CLIPS / f"scene_{idx}_loop_list.txt"
        with open(listfile, "w", encoding="utf-8") as f:
            for i in range(loops):
                f.write(f"file '{raw.resolve()}'\n")
        tmp_concat = CLIPS / f"scene_{idx}_concat.mp4"
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listfile), "-c","copy", str(tmp_concat)], check=True)
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(tmp_concat), "-t", str(target), "-vf","scale=1280:720,setsar=1","-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(proc)], check=True)
        try:
            tmp_concat.unlink()
            listfile.unlink()
        except:
            pass
    else:
        print("[WARN] Could not get duration of downloaded clip; creating a simple color clip.")
        # create color clip placeholder
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=0x123456:s=1280x720:d="+str(target), "-c:v","libx264","-pix_fmt","yuv420p", str(proc)], check=True)
    print(f"[OK] prepared clip for scene {idx} -> {proc.name}")
    time.sleep(0.7)
