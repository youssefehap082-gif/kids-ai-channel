import os, requests, random
from typing import List, Dict
from tenacity import retry, wait_exponential, stop_after_attempt

PEXELS = "https://api.pexels.com/videos/search"
PIXABAY = "https://pixabay.com/api/videos/"

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")

HEADERS = {"Authorization": PEXELS_KEY}

def build_queries(animal: str) -> List[str]:
    words = ["animal", "wildlife", "close up", "nature", "habitat", "4k", "b-roll"]
    return [f"{animal} {w}" for w in words] + [animal]

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def pexels_search(q: str, per_page=10) -> List[Dict]:
    if not PEXELS_KEY: return []
    r = requests.get(PEXELS, headers=HEADERS, params={"query": q, "per_page": per_page})
    r.raise_for_status()
    return r.json().get("videos", [])

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def pixabay_search(q: str, per_page=10) -> List[Dict]:
    if not PIXABAY_KEY: return []
    r = requests.get(PIXABAY, params={"key": PIXABAY_KEY, "q": q, "video_type": "all", "per_page": per_page})
    r.raise_for_status()
    return r.json().get("hits", [])

def pick_video_urls(animal: str, need=8, prefer_vertical=False) -> List[str]:
    urls = []
    target_ratio = (9/16) if prefer_vertical else (16/9)
    for q in build_queries(animal):
        for v in pexels_search(q, per_page=15):
            files = v.get("video_files", [])
            files = sorted(
                files,
                key=lambda x: abs((x["height"]/max(1, x["width"])) - target_ratio)
            )
            if files:
                urls.append(files[0]["link"])
        for h in pixabay_search(q, per_page=15):
            videos = h.get("videos", {})
            for k in ["large", "medium", "small"]:
                if k in videos:
                    urls.append(videos[k]["url"])
                    break
        if len(urls) >= need: break
    random.shuffle(urls)
    return urls[:need]
