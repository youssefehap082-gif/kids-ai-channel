import os
import json
import requests
from pathlib import Path

TMP_DIR = Path("scripts/tmp")

def ensure_tmp():
    """Create temporary folder if it doesn't exist."""
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    return TMP_DIR

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -----------------------------
# FETCH CLIPS FROM PEXELS/PIXABAY
# -----------------------------
def fetch_clips_for_animal(animal: str, limit=5):
    """Return a list of downloadable MP4 URLs from Pexels / Pixabay."""
    results = []

    # PEXELS
    pexels_key = os.getenv("PEXELS_API_KEY")
    if pexels_key:
        try:
            url = f"https://api.pexels.com/videos/search?query={animal}&per_page={limit}"
            r = requests.get(url, headers={"Authorization": pexels_key}, timeout=10)
            data = r.json()
            for video in data.get("videos", []):
                if video["video_files"]:
                    link = video["video_files"][0]["link"]
                    if link.endswith(".mp4"):
                        results.append(link)
        except:
            pass

    # PIXABAY
    pixabay_key = os.getenv("PIXABAY_API_KEY")
    if pixabay_key:
        try:
            url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q={animal}"
            r = requests.get(url, timeout=10)
            data = r.json()
            for hit in data.get("hits", []):
                if hit["videos"]["medium"]["url"]:
                    link = hit["videos"]["medium"]["url"]
                    if link.endswith(".mp4"):
                        results.append(link)
        except:
            pass

    return results[:limit]

# -----------------------------
# ANIMAL DATABASE HELPERS
# -----------------------------
def load_animal_database():
    db_path = Path("data/animal_database.json")
    if not db_path.exists():
        return {}
    return read_json(db_path)

def save_animal_database(data):
    db_path = Path("data/animal_database.json")
    write_json(db_path, data)
