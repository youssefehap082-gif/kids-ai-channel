#!/usr/bin/env python3
# scripts/download_and_prepare_clips.py
# Strict Pexels only: download video for each scene, trim/loop to match audio.
import os, json, time, math, random, requests, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CLIPS = ROOT / "clips"
CLIPS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY","").strip()
if not PEXELS_KEY:
    print("ERROR: PEXELS_API_KEY missing. Set it in Secrets.")
    raise SystemExit(1)

def run(cmd):
    print("RUN:", cmd)
    subprocess.run(cmd, shell=True, check=True)

def get_audio_duration(fp):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                       "-of","default=noprint_wrappers=1:nokey=1", str(fp)], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except:
        return None

def download_url(url, dest):
    print("Downloading:", url)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
    return True

def search_pexels_videos(query, per_page=15):
    try:
        r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization":PEXELS_KEY}, params={"query":query,"per_page":per_page,"size":"medium"}, timeout=30)
        if r.status_code == 200:
            return r.json().get("videos", [])
        else:
            print("Pexels API status", r.status_code, r.text[:200])
    except Exception as e:
        print("Pexels API error:", e)
    return []

def prepare_scene_clip(idx, query, audio_path):
    target = get_audio_duration(audio_path) or 6.0
    target = max(3.0, target)
    dest = CLIPS / f"scene_{idx}.mp4"
    print(f"[SCENE {idx}] target {target}s query='{query}'")
    videos = search_pexels_videos(query, per_page=20)
    chosen_url = None
    chosen_duration = None
    chosen_file_link = None
    if videos:
        # Prefer file with duration >= target, prefer larger quality
        for v in videos:
            dur = v.get("duration", 0)
            # Inspect video_files for mp4 link
            files = v.get("video_files", [])
            # sort files by width/height/bitrate (if available) to prefer higher quality
            files_sorted = sorted(files, key=lambda x: (x.get("width",0), x.get("height",0), x.get("fps",0)), reverse=True)
            for vf in files_sorted:
                if vf.get("file_type") == "video/mp4":
                    if dur >= target:
                        chosen_file_link = vf.get("link") or vf.get("file_link")
                        chosen_duration = dur
                        break
            if chosen_file_link:
                break
        # if no video >= target, pick the highest quality available and we'll loop it later
        if not chosen_file_link:
            v = videos[0]
            files = v.get("video_files", [])
            if files:
                vf = sorted(files, key=lambda x: (x.get("width",0), x.get("height",0)), reverse=True)[0]
                chosen_file_link = vf.get("link") or vf.get("file_link")
                chosen_duration = v.get("duration", None)
    if chosen_file_link:
        try:
            tmpraw = CLIPS / f"scene_{idx}_raw.mp4"
            download_url(chosen_file_link, tmpraw)
            # measure duration
            vdur = None
            try:
                out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(tmpraw)])
                vdur = float(out.strip())
            except:
                vdur = None
            if vdur and vdur >= target - 0.1:
                run(f"ffmpeg -y -ss 0 -i {tmpraw} -t {target} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -c:a aac -b:a 128k {shlex.quote(str(dest))}")
            elif vdur and vdur > 0:
                loops = math.ceil(target / vdur)
                listfile = CLIPS / f"scene_{idx}_loop.txt"
                with open(listfile, "w", encoding="utf-8") as f:
                    for _ in range(loops):
                        f.write(f"file '{tmpraw.resolve()}'\n")
                tmpconcat = CLIPS / f"scene_{idx}_concat.mp4"
                run(f"ffmpeg -y -f concat -safe 0 -i {listfile} -c copy {tmpconcat}")
                run(f"ffmpeg -y -ss 0 -i {tmpconcat} -t {target} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -c:a aac -b:a 128k {shlex.quote(str(dest))}")
                try:
                    tmpconcat.unlink()
                    listfile.unlink()
                except:
                    pass
            else:
                # unknown duration -> trim to target
                run(f"ffmpeg -y -i {tmpraw} -t {target} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -c:a aac -b:a 128k {shlex.quote(str(dest))}")
            try:
                tmpraw.unlink()
            except:
                pass
            print("[OK] prepared clip for scene", idx)
            return dest
        except Exception as e:
            print("Download/process error:", e)
    # if we reached here, no Pexels video worked => create a simple color clip of target length (no images)
    print(f"[WARN] No Pexels video available for scene {idx}. Creating color fallback clip (no images).")
    run(f"ffmpeg -y -f lavfi -i color=c=0x11121a:s=1280x720:d={target} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(dest))}")
    return dest

def main():
    script_path = OUT / "script.json"
    if not script_path.exists():
        print("Missing output/script.json - run generate_script_facts.py first")
        return
    script = json.load(open(script_path, encoding="utf-8"))
    scenes = script.get("scenes", [])
    for s in scenes:
        idx = s.get("idx")
        query = s.get("query","animal")
        audio = OUT / f"scene_{idx}.mp3"
        prepare_scene_clip(idx, query, audio)
        time.sleep(0.6)

if __name__ == "__main__":
    main()
