#!/usr/bin/env python3
# scripts/download_and_prepare_clips.py
# For each scene in output/script.json: try Pexels videos; if none, try Pixabay videos;
# if still none -> fetch Pexels photos and create slideshow (Ken Burns) to match audio duration.

import os, json, time, math, random, requests, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CLIPS = ROOT / "clips"
CLIPS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY","").strip()
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY","").strip()

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

def download_file(url, dest):
    print("Downloading:", url)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)

def search_pexels_videos(query, per_page=15):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization":PEXELS_KEY}, params={"query":query,"per_page":per_page,"size":"medium"}, timeout=30)
        if r.status_code==200:
            return r.json().get("videos",[])
    except Exception as e:
        print("Pexels videos error:", e)
    return []

def search_pixabay_videos(query, per_page=10):
    if not PIXABAY_KEY:
        return []
    try:
        r = requests.get("https://pixabay.com/api/videos/", params={"key":PIXABAY_KEY,"q":query,"per_page":per_page}, timeout=30)
        if r.status_code==200:
            return r.json().get("hits",[])
    except Exception as e:
        print("Pixabay videos error:", e)
    return []

def search_pexels_images(query, per_page=10):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get("https://api.pexels.com/v1/search", headers={"Authorization":PEXELS_KEY}, params={"query":query,"per_page":per_page}, timeout=30)
        if r.status_code==200:
            return r.json().get("photos",[])
    except Exception as e:
        print("Pexels images error:", e)
    return []

def build_slideshow_from_images(img_urls, outpath, duration_sec):
    # download images to temp
    tmpdir = CLIPS / "tmp_imgs"
    tmpdir.mkdir(parents=True, exist_ok=True)
    files = []
    for i, url in enumerate(img_urls[:20]):
        ext = ".jpg"
        p = tmpdir / f"img_{i}{ext}"
        try:
            download_file(url, p)
            files.append(p)
        except Exception as e:
            print("img download error:", e)
    if not files:
        # fallback single color clip
        run(f"ffmpeg -y -f lavfi -i color=c=0x2b2b3a:s=1280x720:d={duration_sec} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(outpath))}")
        return
    # create slideshow using zoompan: each image duration ~ duration_sec/len(files)
    per_img = max(2, int(duration_sec / len(files)))
    listf = tmpdir / "imgs_list.txt"
    with open(listf,"w",encoding="utf-8") as f:
        for p in files:
            f.write(f"file '{p.resolve()}'\n")
            f.write(f"duration {per_img}\n")
    # ffmpeg concat method for images -> produce slideshow, then scale
    tmp_mp4 = tmpdir / "slideshow_tmp.mp4"
    cmd = f"ffmpeg -y -f concat -safe 0 -i {listf} -vsync vfr -pix_fmt yuv420p -vf scale=1280:720 {tmp_mp4}"
    try:
        run(cmd)
        # trim or extend to exact duration
        run(f"ffmpeg -y -i {tmp_mp4} -t {duration_sec} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(outpath))}")
    except Exception as e:
        print("slideshow build error:", e)
        run(f"ffmpeg -y -f lavfi -i color=c=0x2b2b3a:s=1280x720:d={duration_sec} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(outpath))}")

def prepare_scene_clip(idx, query, audio_path):
    target = get_audio_duration(audio_path) or 6.0
    target = max(3.0, target)
    dest = CLIPS / f"scene_{idx}.mp4"
    print(f"[SCENE {idx}] target {target}s query='{query}'")
    # try Pexels videos
    videos = search_pexels_videos(query)
    chosen_url = None
    if videos:
        # pick first mp4 with decent quality and duration
        for v in videos:
            for vf in v.get("video_files",[]):
                if vf.get("file_type")=="video/mp4":
                    if v.get("duration",0) >= target:
                        chosen_url = vf.get("link")
                        break
            if chosen_url:
                break
        if not chosen_url:
            # pick first available
            v = videos[0]
            chosen_url = v.get("video_files",[{}])[0].get("link")
    if chosen_url:
        try:
            tmpraw = CLIPS / f"scene_{idx}_raw.mp4"
            download_file(chosen_url, tmpraw)
            # trim/loop to target
            try:
                vdur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(tmpraw)]).strip())
            except:
                vdur = None
            if vdur and vdur >= target - 0.1:
                run(f"ffmpeg -y -ss 0 -i {tmpraw} -t {target} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -c:a aac -b:a 128k {shlex.quote(str(dest))}")
            elif vdur and vdur > 0:
                loops = math.ceil(target / vdur)
                listfile = CLIPS / f"scene_{idx}_loop.txt"
                with open(listfile,"w",encoding="utf-8") as f:
                    for _ in range(loops):
                        f.write(f"file '{tmpraw.resolve()}'\n")
                tmpconcat = CLIPS / f"scene_{idx}_concat.mp4"
                run(f"ffmpeg -y -f concat -safe 0 -i {listfile} -c copy {tmpconcat}")
                run(f"ffmpeg -y -ss 0 -i {tmpconcat} -t {target} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -c:a aac -b:a 128k {shlex.quote(str(dest))}")
                listfile.unlink(missing_ok=True)
                tmpconcat.unlink(missing_ok=True)
            else:
                run(f"ffmpeg -y -f lavfi -i color=c=0x2b2b3a:s=1280x720:d={target} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(dest))}")
            try:
                tmpraw.unlink(missing_ok=True)
            except:
                pass
            print("[OK] downloaded video for scene", idx)
            return dest
        except Exception as e:
            print("Video download/process error:", e)
    # try Pixabay videos
    hits = search_pixabay_videos(query)
    if hits:
        for h in hits:
            files = h.get("videos",{})
            # pick large if exists
            if files:
                fileinfo = files.get("large") or list(files.values())[0]
                url = fileinfo.get("url")
                try:
                    tmpraw = CLIPS / f"scene_{idx}_rawpix.mp4"
                    download_file(url, tmpraw)
                    run(f"ffmpeg -y -ss 0 -i {tmpraw} -t {target} -vf scale=1280:720,setsar=1 -c:v libx264 -preset fast -c:a aac -b:a 128k {shlex.quote(str(dest))}")
                    tmpraw.unlink(missing_ok=True)
                    print("[OK] pixabay video for scene", idx)
                    return dest
                except Exception as e:
                    print("Pixabay download error:", e)
    # fallback: images slideshow
    print(f"[WARN] No video found for scene {idx} - building slideshow from images")
    photos = search_pexels_images(query, per_page=12)
    img_urls = []
    for p in photos:
        src = p.get("src",{})
        url = src.get("large") or src.get("original")
        if url:
            img_urls.append(url)
    if not img_urls and PIXABAY_KEY:
        # try Pixabay images
        try:
            r = requests.get("https://pixabay.com/api/", params={"key":PIXABAY_KEY,"q":query,"image_type":"photo","per_page":12}, timeout=20)
            if r.status_code==200:
                for h in r.json().get("hits",[]):
                    img_urls.append(h.get("webformatURL") or h.get("largeImageURL"))
        except Exception as e:
            print("Pixabay images error:", e)
    build_slideshow_from_images(img_urls, dest, int(target))
    return dest

def main():
    script_path = OUT / "script.json"
    if not script_path.exists():
        print("Missing output/script.json - run script generator first")
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
