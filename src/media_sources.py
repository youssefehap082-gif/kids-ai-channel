import os
import requests
from random import shuffle

# Primary APIs
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# Backup / Additional APIs
COVERR_API_KEY = os.getenv("COVERR_API_KEY")
STORYBLOCKS_API_KEY = os.getenv("STORYBLOCKS_API_KEY")
VECTEEZY_API_KEY = os.getenv("VECTEEZY_API_KEY")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
BIK_API_KEY = os.getenv("BIK_API_KEY")

def get_video_urls(query, prefer_vertical=True, limit=10):
    """
    Unified function to fetch high-quality, copyright-free animal videos
    from multiple APIs with fallback if one fails or has no results.
    """

    query = query.replace(" ", "+")
    urls = []

    # 1️⃣ PEXELS
    if PEXELS_API_KEY:
        try:
            r = requests.get(
                f"https://api.pexels.com/videos/search?query={query}&per_page={limit}",
                headers={"Authorization": PEXELS_API_KEY},
                timeout=20
            )
            if r.ok:
                urls += [v["video_files"][0]["link"] for v in r.json()["videos"] if v["video_files"]]
        except Exception:
            pass

    # 2️⃣ PIXABAY
    if PIXABAY_API_KEY and len(urls) < limit:
        try:
            r = requests.get(
                f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query}&per_page={limit}",
                timeout=20
            )
            if r.ok:
                urls += [v["videos"]["medium"]["url"] for v in r.json()["hits"]]
        except Exception:
            pass

    # 3️⃣ COVERr
    if COVERR_API_KEY and len(urls) < limit:
        try:
            r = requests.get(f"https://api.coverr.co/videos?query={query}&limit={limit}",
                             headers={"Authorization": COVERR_API_KEY}, timeout=20)
            if r.ok:
                data = r.json()
                urls += [v["urls"]["mp4"] for v in data["videos"] if "urls" in v]
        except Exception:
            pass

    # 4️⃣ STORYBLOCKS
    if STORYBLOCKS_API_KEY and len(urls) < limit:
        try:
            r = requests.get(
                f"https://api.storyblocks.com/api/v2/videos/search?query={query}&results={limit}",
                headers={"Authorization": f"Bearer {STORYBLOCKS_API_KEY}"},
                timeout=20
            )
            if r.ok:
                urls += [v["preview_url"] for v in r.json().get("results", []) if "preview_url" in v]
        except Exception:
            pass

    # 5️⃣ VECTEEZY
    if VECTEEZY_API_KEY and len(urls) < limit:
        try:
            r = requests.get(
                f"https://api.vecteezy.com/videos?query={query}&limit={limit}",
                headers={"Authorization": f"Bearer {VECTEEZY_API_KEY}"},
                timeout=20
            )
            if r.ok:
                urls += [v["video_url"] for v in r.json().get("data", []) if "video_url" in v]
        except Exception:
            pass

    # 6️⃣ CLOUDINARY
    if CLOUDINARY_API_KEY and len(urls) < limit:
        try:
            r = requests.get(
                f"https://api.cloudinary.com/v1_1/demo/resources/search?expression={query}",
                auth=(CLOUDINARY_API_KEY, ""),
                timeout=20
            )
            if r.ok:
                urls += [v["secure_url"] for v in r.json().get("resources", []) if v["format"] == "mp4"]
        except Exception:
            pass

    # 7️⃣ BIK
    if BIK_API_KEY and len(urls) < limit:
        try:
            r = requests.get(
                f"https://api.bik.io/videos/search?query={query}&limit={limit}",
                headers={"x-api-key": BIK_API_KEY},
                timeout=20
            )
            if r.ok:
                urls += [v["url"] for v in r.json().get("results", [])]
        except Exception:
            pass

    shuffle(urls)
    return urls[:limit]
