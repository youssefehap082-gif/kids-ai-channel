# scripts/music_fetcher.py
import os, json, requests, random
from pathlib import Path

ASSETS_MUSIC = Path("assets/music")
ASSETS_MUSIC.mkdir(parents=True, exist_ok=True)

PIX_KEY = os.environ.get("PIXABAY_API_KEY","").strip()
if PIX_KEY:
    try:
        print("Attempting to fetch music from Pixabay (best-effort).")
        url = "https://pixabay.com/api/videos/"
        params = {"key": PIX_KEY, "q": "relaxing ambient", "per_page": 10}
        r = requests.get(url, params=params, timeout=20)
        if r.status_code == 200:
            data = r.json()
            hits = data.get("hits", [])
            if hits:
                h = hits[0]
                if "videos" in h:
                    files = h["videos"]
                    vfile = files.get("large") or files.get("medium") or next(iter(files.values()))
                    if vfile and vfile.get("url"):
                        dest = ASSETS_MUSIC / f"pixabay_music_{random.randint(1000,9999)}.mp3"
                        download_url = vfile["url"]
                        print("Downloading pixabay music-file:", download_url, "->", dest)
                        rr = requests.get(download_url, stream=True, timeout=60)
                        with open(dest, "wb") as fh:
                            for chunk in rr.iter_content(chunk_size=8192):
                                if chunk:
                                    fh.write(chunk)
                        print("Saved music:", dest)
            else:
                print("No pixabay music hits.")
        else:
            print("Pixabay request failed:", r.status_code, r.text[:200])
    except Exception as e:
        print("Pixabay fetch error:", e)

files = list(ASSETS_MUSIC.glob("*.mp3")) + list(ASSETS_MUSIC.glob("*.wav"))
print("Music files available in assets/music/:", [f.name for f in files])
if not files:
    print("No music files found in assets/music/. You can add royalty-free mp3 files there or add PIXABAY_API_KEY secret.")
