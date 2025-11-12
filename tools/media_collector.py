# tools/media_collector.py
import os, requests, shutil, random
from pathlib import Path

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def download_file(url, out_path, timeout=60):
    try:
        r = requests.get(url, stream=True, timeout=timeout)
        with open(out_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
        return True
    except Exception:
        return False

def fetch_images_and_videos_public(query, out_folder="assets/tmp", needed_images=8, needed_videos=2):
    Path(out_folder).mkdir(parents=True, exist_ok=True)
    images = 0
    videos = 0

    # Pexels images
    if PEXELS_API_KEY:
        headers = {"Authorization": PEXELS_API_KEY}
        page = 1
        while images < needed_images:
            r = requests.get("https://api.pexels.com/v1/search", params={"query":query, "per_page":15, "page":page}, headers=headers, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            for p in data.get("photos", []):
                if images >= needed_images:
                    break
                url = p["src"].get("large") or p["src"].get("original")
                if not url: continue
                fname = Path(out_folder) / f"img_{images}_{p['id']}.jpg"
                if download_file(url, fname):
                    images += 1
            if not data.get("photos"):
                break
            page += 1

    # Pixabay fallback images
    if images < needed_images and PIXABAY_API_KEY:
        r = requests.get("https://pixabay.com/api/", params={"key":PIXABAY_API_KEY, "q":query, "per_page":50, "image_type":"photo"})
        if r.status_code == 200:
            for h in r.json().get("hits", []):
                if images >= needed_images: break
                url = h.get("largeImageURL") or h.get("webformatURL")
                fname = Path(out_folder) / f"img_px_{images}_{h.get('id')}.jpg"
                if download_file(url, fname):
                    images += 1

    # Pexels videos
    if PEXELS_API_KEY:
        headers = {"Authorization": PEXELS_API_KEY}
        r = requests.get("https://api.pexels.com/videos/search", params={"query":query, "per_page":15}, headers=headers, timeout=30)
        if r.status_code == 200:
            for v in r.json().get("videos", []):
                if videos >= needed_videos: break
                files = v.get("video_files", [])
                files = [f for f in files if f.get("file_type") == "video/mp4"]
                if not files: continue
                # pick smallest mp4
                files_sorted = sorted(files, key=lambda x: x.get("width", 9999))
                url = files_sorted[0]["link"]
                fname = Path(out_folder) / f"vid_{videos}_{v['id']}.mp4"
                if download_file(url, fname, timeout=120):
                    videos += 1

    return {"images": images, "videos": videos}
