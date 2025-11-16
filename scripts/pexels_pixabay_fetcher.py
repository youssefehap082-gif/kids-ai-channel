# scripts/pexels_pixabay_fetcher.py
"""
Fetch video clips from Pexels and Pixabay.
- returns local downloaded file paths (list)
- requires PEXELS_API_KEY and PIXABAY_API_KEY in env
"""
import os
import requests
import logging
from pathlib import Path
from scripts.utils import download_file, safe_mkdir

log = logging.getLogger("fetcher")
TMP = Path(__file__).resolve().parent / "tmp"
safe_mkdir(TMP)

PEXELS_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")


def _fetch_from_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={requests.utils.requote_uri(query)}&per_page={per_page}"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        items = r.json().get("videos", [])
        urls = []
        for v in items:
            files = v.get("video_files", [])
            if files:
                urls.append(files[0].get("link"))
        return urls
    except Exception as e:
        log.warning("Pexels failed: %s", e)
        return []


def _fetch_from_pixabay(query, per_page=5):
    if not PIXABAY_KEY:
        return []
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={requests.utils.requote_uri(query)}&per_page={per_page}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        urls = []
        for h in hits:
            vid = h.get("videos", {}).get("large") or h.get("videos", {}).get("medium")
            if vid:
                urls.append(vid.get("url"))
        return urls
    except Exception as e:
        log.warning("Pixabay failed: %s", e)
        return []


def fetch_video_clips(name, count=3, short_mode=False):
    """
    Returns list of local files downloaded.
    Ensures uniqueness and tries both services.
    """
    q = name
    urls = _fetch_from_pexels(q, per_page=6)
    if len(urls) < count:
        urls += _fetch_from_pixabay(q, per_page=6)
    urls = list(dict.fromkeys([u for u in urls if u]))  # unique preserve order

    downloaded = []
    for i, u in enumerate(urls[:count]):
        try:
            dest = TMP / f"{name.replace(' ', '_')}_{i}.mp4"
            download_file(u, dest)
            downloaded.append(dest)
        except Exception as e:
            log.warning("Download failed for %s: %s", u, e)
            continue
    return downloaded
