import requests, os, random
from pathlib import Path

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def get_random_music(out_path="music.mp3"):
    if not PIXABAY_API_KEY:
        return None
    r = requests.get("https://pixabay.com/api/sound/", params={"key":PIXABAY_API_KEY, "q":"background music","per_page":50})
    if r.status_code!=200:
        return None
    hits = r.json().get("hits", [])
    if not hits: return None
    url = random.choice(hits)["audio"]
    data = requests.get(url, timeout=60)
    Path(out_path).write_bytes(data.content)
    return out_path

