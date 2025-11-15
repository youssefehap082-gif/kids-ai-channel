# scripts/pexels_pixabay_fetcher.py
"""
Fetch videos from Pexels and Pixabay for a given animal name.

Provides:
- fetch_media_for_animal(name, max_results=6) -> list[str]

Behavior:
1) Query Pexels videos endpoint (if PEXELS_API_KEY present)
2) Query Pixabay videos endpoint (if PIXABAY_API_KEY present)
3) Download candidate video files into scripts/tmp/
4) If moviepy is available, attempt to open and verify duration > 0.5s
5) Return list of local file paths (strings) that passed basic checks
6) Robust error handling and logging
"""

import os
import requests
import logging
from pathlib import Path
from typing import List, Optional
import time
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parent
TMP = ROOT / "tmp"
TMP.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")

# Helper: stream-download to file
def _download_stream(url: str, dest: Path, headers: Optional[dict] = None, timeout: int = 60) -> Path:
    """
    Download url to dest path streaming. Returns dest Path.
    """
    logger.debug("Downloading %s -> %s", url, dest)
    headers = headers or {}
    with requests.get(url, stream=True, headers=headers, timeout=timeout) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(chunk_size=1024 * 32):
                if chunk:
                    fh.write(chunk)
    return dest

# Helper: try to verify video duration using moviepy (optional)
def _verify_video(path: Path, min_seconds: float = 0.5) -> bool:
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(str(path))
        duration = getattr(clip, "duration", 0) or 0
        clip.close()
        if duration and duration >= min_seconds:
            return True
        else:
            logger.debug("Video %s duration too short: %s", path, duration)
            return False
    except Exception as e:
        # if moviepy not available or opening fails, assume file is OK (non-validated)
        logger.debug("Video verification skipped/failed for %s: %s", path, e)
        # Basic file-size fallback: require > 50 KB
        try:
            if path.exists() and path.stat().st_size > 50 * 1024:
                return True
        except Exception:
            pass
        return False


def _safe_filename(name: str) -> str:
    keep = (" ", ".", "_", "-")
    return "".join(c for c in name if c.isalnum() or c in keep).rstrip()


def _fetch_from_pexels(query: str, per_page: int = 8) -> List[str]:
    """
    Query Pexels videos API and return list of downloadable urls (mp4).
    """
    if not PEXELS_KEY:
        logger.info("PEXELS key not provided; skipping Pexels.")
        return []

    try:
        headers = {"Authorization": PEXELS_KEY}
        url = f"https://api.pexels.com/videos/search?query={requests.utils.requote_uri(query)}&per_page={per_page}"
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        urls = []
        for v in data.get("videos", []):
            # choose best available mp4 (prefer 'sd' or 'video_files' list first)
            files = v.get("video_files", [])
            if not files:
                continue
            # pick the file with highest width but reasonable size
            files_sorted = sorted(files, key=lambda f: (f.get("width", 0), -f.get("fps", 0)), reverse=True)
            for f in files_sorted:
                link = f.get("link")
                if link and link.endswith(".mp4"):
                    urls.append(link)
                    break
        logger.info("Pexels returned %d candidate URLs for query '%s'", len(urls), query)
        return urls
    except Exception as e:
        logger.warning("Pexels fetch failed for query '%s': %s", query, e)
        return []


def _fetch_from_pixabay(query: str, per_page: int = 8) -> List[str]:
    """
    Query Pixabay video API and return list of downloadable urls (mp4).
    """
    if not PIXABAY_KEY:
        logger.info("PIXABAY key not provided; skipping Pixabay.")
        return []

    try:
        url = "https://pixabay.com/api/videos/"
        params = {"key": PIXABAY_KEY, "q": query, "per_page": per_page}
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        urls = []
        for hit in data.get("hits", []):
            # choose large if present
            videos = hit.get("videos", {})
            # priorities: large -> medium -> small
            for size in ("large", "medium", "small"):
                s = videos.get(size)
                if s and s.get("url"):
                    urls.append(s["url"])
                    break
        logger.info("Pixabay returned %d candidate URLs for query '%s'", len(urls), query)
        return urls
    except Exception as e:
        logger.warning("Pixabay fetch failed for query '%s': %s", query, e)
        return []


def fetch_media_for_animal(animal_name: str, max_results: int = 6) -> List[str]:
    """
    Main function — returns local file paths to downloaded video clips for an animal.
    Steps:
      1) Query Pexels
      2) Query Pixabay
      3) Shuffle combined candidates
      4) Download up to max_results unique files to scripts/tmp/
      5) Verify downloaded files (moviepy or filesize)
    """
    start = time.time()
    logger.info("Fetching media for animal: %s", animal_name)
    q = f"{animal_name} animal"

    candidates = []
    # try Pexels first (higher quality)
    try:
        pex_urls = _fetch_from_pexels(q, per_page=max_results * 2)
        candidates.extend(pex_urls)
    except Exception:
        pass

    # then Pixabay
    try:
        pix_urls = _fetch_from_pixabay(q, per_page=max_results * 2)
        candidates.extend(pix_urls)
    except Exception:
        pass

    # If nothing found, broaden query to just animal name
    if not candidates:
        if PEXELS_KEY:
            candidates.extend(_fetch_from_pexels(animal_name, per_page=max_results))
        if not candidates and PIXABAY_KEY:
            candidates.extend(_fetch_from_pixabay(animal_name, per_page=max_results))

    # dedupe while preserving order
    seen = set()
    candidates_unique = []
    for u in candidates:
        if u not in seen:
            candidates_unique.append(u)
            seen.add(u)

    random.shuffle(candidates_unique)

    downloaded = []
    for i, url in enumerate(candidates_unique):
        if len(downloaded) >= max_results:
            break
        try:
            ext = ".mp4"
            safe_name = _safe_filename(f"{animal_name}_{i}")
            dest = TMP / f"{safe_name}{ext}"
            # avoid re-downloading same url if exists (simple: check file exists)
            if dest.exists() and dest.stat().st_size > 1000:
                if _verify_video(dest):
                    downloaded.append(str(dest))
                    continue
                else:
                    try:
                        dest.unlink()
                    except Exception:
                        pass

            # download
            _download_stream(url, dest, headers=None, timeout=90)

            # basic verify
            if _verify_video(dest):
                downloaded.append(str(dest))
            else:
                logger.info("Downloaded file failed verification: %s", dest)
                try:
                    dest.unlink()
                except Exception:
                    pass

        except Exception as e:
            logger.warning("Failed to download candidate %s: %s", url, e)
            continue

    elapsed = time.time() - start
    logger.info("fetch_media_for_animal finished: found %d clips in %.1fs", len(downloaded), elapsed)
    return downloaded
