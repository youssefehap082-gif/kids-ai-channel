#!/usr/bin/env python3
# scripts/download_and_prepare_clips.py
import os, json, time, math, requests, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CLIPS_DIR = ROOT / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY", "").strip()

MIN_DURATION = int(os.environ.get("MIN_DURATION", "180"))

def run(cmd):
    print("RUN:", cmd)
    subprocess.run(cmd, shell=True, check=True)

def get_duration(path):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(path)], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except:
        return 0.0

def download_stream(url, dest_path):
    print("Downloading:", url)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as fh:
            for chunk in r.iter_content(1024*16):
                if chunk:
                    fh.write(chunk)

def search_pexels_videos(query, per_page=30):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization":PEXELS_KEY}, params={"query":query,"per_page":per_page,"size":"medium"}, timeout=30)
        if r.status_code == 200:
            return r.json().get("videos", [])
        else:
            print("Pexels API status", r.status_code, r.text[:300])
    except Exception as e:
        print("Pexels API error:", e)
    return []

def pick_mp4_from_pexels(entry):
    files = entry.get("video_files", [])
    files_sorted = sorted(files, key=lambda x: (x.get("width",0), x.get("height",0)), reverse=True)
    for f in files_sorted:
        if f.get("file_type") == "video/mp4" and f.get("link"):
            return f.get("link"), entry.get("duration", None)
    return None, None

def search_pixabay_videos(query, per_page=50):
    if not PIXABAY_KEY:
        return []
    try:
        r = requests.get("https://pixabay.com/api/videos/", params={"key":PIXABAY_KEY,"q":query,"per_page":per_page}, timeout=30)
        if r.status_code == 200:
            return r.json().get("hits", [])
        else:
            print("Pixabay API status", r.status_code, r.text[:300])
    except Exception as e:
        print("Pixabay API error:", e)
    return []

def pick_mp4_from_pixabay(entry):
    videos = entry.get("videos", {})
    for key in ("large","medium","small"):
        v = videos.get(key)
        if v and v.get("url"):
            return v.get("url"), entry.get("duration", None)
    for v in videos.values():
        if v.get("url"):
            return v.get("url"), entry.get("duration", None)
    return None, None

def transcode_standard(src, dst):
    cmd = f"ffmpeg -y -ss 0 -i {shlex.quote(str(src))} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k {shlex.quote(str(dst))}"
    run(cmd)

def ensure_enough_clips(target_seconds, queries):
    acc = 0.0
    produced = []
    idx = 0

    def add_from_url(url, est_dur=None):
        nonlocal idx, acc
        idx += 1
        raw = CLIPS_DIR / f"part_{idx}_raw.mp4"
        std = CLIPS_DIR / f"part_{idx}.mp4"
        try:
            download_stream(url, raw)
            transcode_standard(raw, std)
            dur = get_duration(std)
            if dur <= 0 and est_dur:
                dur = est_dur
            acc += dur
            produced.append(std)
            try:
                raw.unlink()
            except:
                pass
            print(f"[PART] added {std.name} dur={dur:.1f}s total={acc:.1f}s")
            return True
        except Exception as e:
            print("Failed to process url:", e)
            try:
                raw.unlink()
            except:
                pass
            return False

    # try pexels first
    for q in queries:
        if acc >= target_seconds:
            break
        videos = search_pexels_videos(q, per_page=30)
        for e in videos:
            if acc >= target_seconds:
                break
            url, dur = pick_mp4_from_pexels(e)
            if url:
                ok = add_from_url(url, est_dur=dur)
                if not ok:
                    continue

    # if still short, try pixabay
    if acc < target_seconds and PIXABAY_KEY:
        for q in queries:
            if acc >= target_seconds:
                break
            hits = search_pixabay_videos(q, per_page=50)
            for e in hits:
                if acc >= target_seconds:
                    break
                url, dur = pick_mp4_from_pixabay(e)
                if url:
                    ok = add_from_url(url, est_dur=dur)
                    if not ok:
                        continue

    # if still less but have produced parts, loop copies to fill
    if acc < target_seconds and produced:
        print("[INFO] looping produced parts to reach target")
        loop_i = 0
        while acc < target_seconds:
            src = produced[loop_i % len(produced)]
            loop_i += 1
            idx += 1
            copy_path = CLIPS_DIR / f"part_{idx}.mp4"
            run(f"cp {shlex.quote(str(src))} {shlex.quote(str(copy_path))}")
            dur = get_duration(copy_path)
            acc += dur
            produced.append(copy_path)
            print(f"[LOOP] added copy {copy_path.name} dur={dur:.1f}s total={acc:.1f}s")
    return produced, acc

def concat_parts(parts, out_file):
    listf = CLIPS_DIR / "concat_parts.txt"
    with open(listf, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.resolve()}'\n")
    run(f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(listf))} -c copy {shlex.quote(str(out_file))}")
    try:
        listf.unlink()
    except:
        pass

def main():
    script_path = OUT / "script.json"
    if not script_path.exists():
        print("Missing output/script.json")
        return
    script = json.load(open(script_path, encoding="utf-8"))
    animal = script.get("animal_key", "animal")
    queries = [animal]
    for s in script.get("scenes", []):
        q = s.get("query")
        if q and q not in queries:
            queries.append(q)
    narration = OUT / "narration_full.mp3"
    narr_dur = get_duration(narration) if narration.exists() else 0.0
    target = max(MIN_DURATION, int(math.ceil(narr_dur)))
    print(f"Target seconds = max(MIN_DURATION={MIN_DURATION}, narration={narr_dur}) => {target}s")
    parts, total = ensure_enough_clips(target, queries)
    if not parts:
        print("[ERROR] no clips produced from Pexels/Pixabay. Exiting.")
        return
    combined = CLIPS_DIR / "combined_clips.mp4"
    concat_parts(parts, combined)
    print("Combined created:", combined, "duration", get_duration(combined))

if __name__ == "__main__":
    main()
