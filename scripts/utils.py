# scripts/utils.py
import os
import json
import logging
import time
import random
import requests
from pathlib import Path

# ---------------------------------------------------
# Global Paths
# ---------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TMP = ROOT / "tmp"
ASSETS = ROOT / "assets"
MUSIC = ASSETS / "music"

DATA.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)
MUSIC.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------
# Global Logger
# ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)
logger = logging.getLogger("utils")


# ---------------------------------------------------
# JSON Helpers
# ---------------------------------------------------
def jload(path, default=None):
    try:
        if path.exists():
            return json.loads(path.read_text())
        return default
    except:
        return default


def jsave(path, data):
    path.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------
# Retry Helper
# ---------------------------------------------------
def retry(times, wait, fn, *args, **kwargs):
    """
    Retry a function up to `times` with waiting seconds.
    If fn raises error, waits and tries again.
    """
    for attempt in range(times):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == times - 1:
                raise
            time.sleep(wait)


# ---------------------------------------------------
# File Helpers
# ---------------------------------------------------
def safe_name(text):
    return "".join(c for c in text if c.isalnum() or c in (' ','_','-','.')).strip()


def unique_filename(base, ext=".mp4"):
    t = int(time.time())
    r = random.randint(1000, 9999)
    return f"{safe_name(base)}_{t}_{r}{ext}"


# ---------------------------------------------------
# Download File Helper
# ---------------------------------------------------
def download_file(url, dest: Path):
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1024 * 32):
                if chunk:
                    f.write(chunk)
    return dest


# ---------------------------------------------------
# Fetch No-Copyright Music
# ---------------------------------------------------
PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")

def fetch_music():
    """
    Fetch copyright-free music from Pixabay.
    If fails → fallback to a local silent audio.
    """

    # 1) Try Pixabay Music API
    if PIXABAY_KEY:
        try:
            url = "https://pixabay.com/api/sound/"
            params = {
                "key": PIXABAY_KEY,
                "q": "background",
                "per_page": 20
            }
            r = requests.get(url, params=params, timeout=20)
            data = r.json()

            hits = data.get("hits", [])
            if hits:
                track = random.choice(hits)
                src = track.get("audio", "")
                if src:
                    dest = TMP / unique_filename("bgmusic", ".mp3")
                    download_file(src, dest)
                    return str(dest)
        except Exception as e:
            logger.warning("Pixabay music fetch failed: %s", e)

    # 2) Pexels (less common for audio but try anyway)
    if PEXELS_KEY:
        try:
            headers = {"Authorization": PEXELS_KEY}
            url = "https://api.pexels.com/v1/search?query=music"
            r = requests.get(url, headers=headers, timeout=20)
            # Not guaranteed to have audio, skip
        except:
            pass

    # 3) Last fallback: generate silent audio file (2 seconds)
    silent = TMP / "silent.mp3"
    if not silent.exists():
        # generate blank audio
        import wave
        import struct
        framerate = 44100
        duration = 2
        nframes = duration * framerate
        with wave.open(str(silent), "w") as w:
            w.setparams((1, 2, framerate, nframes, "NONE", "not compressed"))
            for _ in range(nframes):
                value = 0
                data = struct.pack('<h', value)
                w.writeframesraw(data)

    return str(silent)


# ---------------------------------------------------
# Add watermark helper
# ---------------------------------------------------
def build_watermark_text(animal_name):
    base = "@WildPlanetFacts"
    return f"{base} · {animal_name.capitalize()}"
