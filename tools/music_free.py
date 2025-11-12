# tools/music_free.py
import os, requests, random
from pathlib import Path

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def get_random_music(out_path="music.mp3"):
    if not PIXABAY_API_KEY:
        return None
    try:
        r = requests.get("https://pixabay.com/api/sounds/", params={"key":PIXABAY_API_KEY, "q":"background", "per_page":50})
        if r.status_code != 200:
            return None
        hits = r.json().get("hits", [])
        if not hits:
            return None
        pick = random.choice(hits)
        url = pick.get("audio")
        if not url:
            return None
        data = requests.get(url, timeout=60)
        Path(out_path).write_bytes(data.content)
        return out_path
    except Exception:
        return None
