#!/usr/bin/env python3
# scripts/download_and_prepare_clips.py
# STRICT: prefer Pexels, then Pixabay. Do NOT use images as fallback.
# Assemble multiple clips (transcode to uniform format) until total >= target_total (default 180s)
# Produces: clips/combined_clips.mp4

import os, json, time, math, requests, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CLIPS_DIR = ROOT / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY", "").strip()

MIN_DURATION = int(os.environ.get("MIN_DURATION", "180"))  # seconds, default 180s (3 minutes)

def run(cmd):
    print("RUN:", cmd)
    subprocess.run(cmd, shell=True, check=True)

def get_audio_duration(path):
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except Exception:
        return 0.0

def transcode_to_standard(src_path, dst_path, duration=None):
    # produce mp4 1280x720 libx264 + aac
    dur_arg = f"-t {duration}" if duration else ""
    cmd = f"ffmpeg -y -ss 0 -i {shlex.quote(str(src_path))} {dur_arg} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k {shlex.quote(str(dst_path))}"
    run(cmd)

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
        r = requests.get("https://api.pexels.com/videos/search",
                         headers={"Authorization": PEXELS_KEY},
                         params={"query": query, "per_page": per_page, "size": "medium"},
                         timeout=30)
        if r.status_code == 200:
            return r.json().get("videos", [])
        else:
            print("PEXELS API error:", r.status_code, r.text[:300])
    except Exception as e:
        print("PEXELS exception:", e)
    return []

def search_pixabay_videos(query, per_page=50):
    if not PIXABAY_KEY:
        return []
    try:
        r = requests.get("https://pixabay.com/api/videos/",
                         params={"key": PIXABAY_KEY, "q": query, "per_page": per_page},
                         timeout=30)
        if r.status_code == 200:
            return r.json().get("hits", [])
        else:
            print("PIXABAY API error:", r.status_code, r.text[:300])
    except Exception as e:
        print("PIXABAY exception:", e)
    return []

def pick_mp4_link_from_pexels_entry(entry):
    files = entry.get("video_files", [])
    # sort prefer larger resolution
    files_sorted = sorted(files, key=lambda x: (x.get("width", 0), x.get("height", 0), x.get("fps", 0)), reverse=True)
    for f in files_sorted:
        if f.get("file_type") == "video/mp4" and f.get("link"):
            return f.get("link"), entry.get("duration", None)
    return None, None

def pick_mp4_link_from_pixabay_entry(entry):
    videos = entry.get("videos", {})
    # prefer 'large' then others
    for key in ("large", "medium", "small"):
        v = videos.get(key)
        if v and v.get("url"):
            return v.get("url"), entry.get("duration", None)
    # else try any
    for v in videos.values():
        if v.get("url"):
            return v.get("url"), entry.get("duration", None)
    return None, None

def ensure_enough_clips(target_seconds, queries):
    """
    Collect clips into CLIPS_DIR/part_*.mp4 transcoded to standard format,
    until accumulated duration >= target_seconds.
    Returns list of produced clip paths and accumulated duration.
    """
    accumulated = 0.0
    produced = []
    idx = 0

    # Helper to process a candidate url
    def process_candidate(url, est_dur=None):
        nonlocal idx, accumulated
        idx += 1
        raw = CLIPS_DIR / f"part_{idx}_raw.mp4"
        std = CLIPS_DIR / f"part_{idx}.mp4"
        try:
            download_stream(url, raw)
            # transcode to standard, but trim if very long (we can trim later)
            transcode_to_standard(raw, std)
            dur = get_audio_duration(std)  # works for video too
            if not dur:
                dur = est_dur or 0.0
            accumulated += dur
            produced.append(std)
            try:
                raw.unlink()
            except:
                pass
            print(f"[PART] added {std.name} dur={dur:.1f}s total={accumulated:.1f}s")
            return True
        except Exception as e:
            print("Candidate processing failed:", e)
            try:
                raw.unlink(missing_ok=True)
            except:
                pass
            return False

    # 1) try Pexels for each query
    for q in queries:
        if accumulated >= target_seconds:
            break
        videos = search_pexels_videos(q, per_page=30)
        for entry in videos:
            if accumulated >= target_seconds:
                break
            link, dur = pick_mp4_link_from_pexels_entry(entry)
            if link:
                try:
                    ok = process_candidate(link, est_dur=dur)
                    if not ok:
                        continue
                except Exception:
                    continue

    # 2) if still not enough, try Pixabay with same queries
    if accumulated < target_seconds and PIXABAY_KEY:
        for q in queries:
            if accumulated >= target_seconds:
                break
            hits = search_pixabay_videos(q, per_page=50)
            for entry in hits:
                if accumulated >= target_seconds:
                    break
                link, dur = pick_mp4_link_from_pixabay_entry(entry)
                if link:
                    try:
                        ok = process_candidate(link, est_dur=dur)
                        if not ok:
                            continue
                    except Exception:
                        continue

    # 3) if still not enough but we have some produced clips -> loop them (concatenate repeats)
    if accumulated < target_seconds and produced:
        print("[INFO] Not enough unique clips, will loop existing parts to reach target.")
        loop_idx = 0
        while accumulated < target_seconds:
            src = produced[loop_idx % len(produced)]
            loop_idx += 1
            idx += 1
            copy_path = CLIPS_DIR / f"part_{idx}.mp4"
            # copy src to new file (no re-encode)
            try:
                run(f"cp {shlex.quote(str(src))} {shlex.quote(str(copy_path))}")
                dur = get_audio_duration(copy_path) or 0.0
                accumulated += dur
                produced.append(copy_path)
                print(f"[LOOP] copied {copy_path.name} dur={dur:.1f}s total={accumulated:.1f}s")
            except Exception as e:
                print("Loop copy failed:", e)
                break

    # 4) if still nothing produced at all -> return empty
    return produced, accumulated

def concat_parts_to_combined(parts, out_combined):
    if not parts:
        return False
    list_txt = CLIPS_DIR / "concat_list.txt"
    with open(list_txt, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.resolve()}'\n")
    # concat with ffmpeg copy (parts have same codec because we transcoded)
    cmd = f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(list_txt))} -c copy {shlex.quote(str(out_combined))}"
    run(cmd)
    try:
        list_txt.unlink()
    except:
        pass
    return True

def main():
    script_path = OUT / "script.json"
    if not script_path.exists():
        print("Missing output/script.json - run generate_script_facts.py first")
        return

    script = json.load(open(script_path, encoding="utf-8"))
    animal = script.get("animal_key", "animal")
    # build queries list (prioritize animal + specific scene queries)
    queries = []
    # add animal_key and title-based queries
    queries.append(animal)
    # include scene-specific queries if present (script['scenes'][i]['query'])
    for s in script.get("scenes", []):
        q = s.get("query")
        if q and q not in queries:
            queries.append(q)

    # narration duration (if exists)
    narration = OUT / "narration_full.mp3"
    narration_dur = get_audio_duration(narration) if narration.exists() else 0.0
    target_total = max(MIN_DURATION, int(math.ceil(narration_dur)))
    print(f"Target total duration (seconds): MIN_DURATION={MIN_DURATION}, narration_dur={narration_dur:.1f} => target_total={target_total}")

    # collect parts until reach target_total
    parts, acc = ensure_enough_clips(target_total, queries)

    if not parts:
        print("[ERROR] No parts produced from Pexels/Pixabay. Creating a single color fallback clip of target length.")
        out_combined = CLIPS_DIR / "combined_clips.mp4"
        run(f"ffmpeg -y -f lavfi -i color=c=0x0f2130:s=1280x720:d={target_total} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(out_combined))}")
        print("Fallback created:", out_combined)
        return

    # if accumulated parts < target_total still (rare), we can trim last part to exact remaining seconds
    total_dur = sum([get_audio_duration(p) for p in parts])
    if total_dur < target_total:
        print(f"[INFO] total_dur {total_dur:.1f} < target {target_total}, will loop last part to fill (should be handled earlier).")
    # if total_dur > target_total, we should trim last part to fit exactly
    if total_dur > target_total:
        # find amount to trim from last part
        excess = total_dur - target_total
        # trim last part: create trimmed copy
        last = parts[-1]
        last_dur = get_audio_duration(last)
        keep = last_dur - excess
        if keep <= 0:
            print("[WARN] cannot trim last part to negative keep, skipping trim.")
        else:
            trimmed = CLIPS_DIR / f"{last.stem}_trim.mp4"
            run(f"ffmpeg -y -ss 0 -i {shlex.quote(str(last))} -t {keep} -c copy {shlex.quote(str(trimmed))}")
            # replace last entry
            parts[-1] = trimmed
            try:
                last.unlink(missing_ok=True)
            except:
                pass
            print(f"Trimmed last part to {keep:.1f}s to fit total {target_total}s")

    # concat parts
    out_combined = CLIPS_DIR / "combined_clips.mp4"
    success = concat_parts_to_combined(parts, out_combined)
    if success:
        final_dur = get_audio_duration(out_combined)
        print("Combined clip created:", out_combined, "duration:", final_dur)
    else:
        print("[ERROR] concat failed.")
    return

if __name__ == "__main__":
    main()
