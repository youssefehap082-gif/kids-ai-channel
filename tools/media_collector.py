# tools/media_collector.py
import os, requests, shutil
from pathlib import Path

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def fetch_images_and_videos(query, out_folder="assets/tmp", needed_images=8, needed_videos=2):
    Path(out_folder).mkdir(parents=True, exist_ok=True)
    # 1) Try Pexels images
    headers = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}
    images_downloaded = 0
    page = 1
    while images_downloaded < needed_images and PEXELS_API_KEY:
        r = requests.get("https://api.pexels.com/v1/search", params={"query": query, "per_page":15, "page":page}, headers=headers, timeout=30)
        if r.status_code!=200:
            break
        data = r.json()
        for photo in data.get("photos",[]):
            url = photo["src"]["large"]
            fname = Path(out_folder)/f"img_{images_downloaded}_{photo['id']}.jpg"
            if not fname.exists():
                try:
                    dl = requests.get(url, stream=True, timeout=30)
                    with open(fname,"wb") as f:
                        shutil.copyfileobj(dl.raw, f)
                    images_downloaded +=1
                except: pass
            if images_downloaded>=needed_images:
                break
        page +=1

    # fallback using Pixabay if not enough
    if images_downloaded < needed_images and PIXABAY_API_KEY:
        r = requests.get("https://pixabay.com/api/", params={"key":PIXABAY_API_KEY,"q":query,"image_type":"photo","per_page":50})
        if r.status_code==200:
            for hit in r.json().get("hits",[]):
                if images_downloaded>=needed_images: break
                url = hit.get("largeImageURL")
                fname = Path(out_folder)/f"img_pix_{images_downloaded}_{hit.get('id')}.jpg"
                try:
                    dl = requests.get(url, stream=True, timeout=30)
                    with open(fname,"wb") as f:
                        shutil.copyfileobj(dl.raw,f)
                    images_downloaded+=1
                except: pass

    # Videos: try Pexels videos
    videos_downloaded = 0
    if PEXELS_API_KEY:
        r = requests.get("https://api.pexels.com/videos/search", params={"query":query, "per_page":10}, headers=headers, timeout=30)
        if r.status_code==200:
            for v in r.json().get("videos",[]):
                if videos_downloaded>=needed_videos: break
                files = v.get("video_files",[])
                # pick smallest mp4
                files = sorted([f for f in files if f.get("file_type")== "video/mp4"], key=lambda x: x.get("width",0))
                if not files: continue
                url = files[0]["link"]
                fname = Path(out_folder)/f"vid_{videos_downloaded}_{v['id']}.mp4"
                try:
                    dl = requests.get(url, stream=True, timeout=60)
                    with open(fname,"wb") as f:
                        shutil.copyfileobj(dl.raw,f)
                    videos_downloaded+=1
                except: pass

    return {"images": images_downloaded, "videos": videos_downloaded}
