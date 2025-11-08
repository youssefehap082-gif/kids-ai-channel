import os, requests, random, re
from typing import List, Dict
from tenacity import retry, wait_exponential, stop_after_attempt

PEXELS = "https://api.pexels.com/videos/search"
PIXABAY = "https://pixabay.com/api/videos/"

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")

HEADERS = {"Authorization": PEXELS_KEY}

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", s.lower()).strip()

def _matches(animal: str, *fields: str) -> bool:
    a = _norm(animal)
    return any(a in _norm(x) for x in fields if x)

def build_queries(animal: str) -> List[str]:
    # ابحث بالاسم مباشرة + صيغة جمع/مفرد
    return [animal, f"{animal} animal", f"{animal} wildlife"]

@retry(wait=wait_exponential(min=1, max=6), stop=stop_after_attempt(2))
def pexels_search(q: str, per_page=12) -> List[Dict]:
    if not PEXELS_KEY: return []
    r = requests.get(PEXELS, headers=HEADERS, params={"query": q, "per_page": per_page})
    r.raise_for_status()
    return r.json().get("videos", [])

@retry(wait=wait_exponential(min=1, max=6), stop=stop_after_attempt(2))
def pixabay_search(q: str, per_page=12) -> List[Dict]:
    if not PIXABAY_KEY: return []
    r = requests.get(PIXABAY, params={"key": PIXABAY_KEY, "q": q, "video_type": "all", "per_page": per_page})
    r.raise_for_status()
    return r.json().get("hits", [])

def pick_video_urls(animal: str, need=8, prefer_vertical=False) -> List[str]:
    urls = []
    target_ratio = (9/16) if prefer_vertical else (16/9)

    for q in build_queries(animal):
        # PEXELS
        for v in pexels_search(q):
            files = v.get("video_files", [])
            url = None
            if files:
                files = sorted(files, key=lambda x: abs((x["height"]/max(1, x["width"])) - target_ratio))
                # فلترة بالـurl/الـuser/الـid (أفضل المتاح)
                candidate = files[0]["link"]
                if _matches(animal, candidate, q):
                    url = candidate
            if url: urls.append(url)

        # PIXABAY (الأفضل من حيث tags)
        for h in pixabay_search(q):
            tags = h.get("tags", "")
            videos = h.get("videos", {})
            chosen = None
            for k in ["large", "medium", "small"]:
                if k in videos:
                    chosen = videos[k]["url"]
                    break
            if chosen and _matches(animal, tags, chosen, q):
                urls.append(chosen)

        if len(urls) >= need:
            break

    random.shuffle(urls)
    # لو النتائج قليلة جدًا، خُد أي حاجة كملء فراغ بدل ما يفشل
    if len(urls) < max(3, need//2):
        fallback = [u for u in urls]
        urls = (urls + fallback)[:need]
    return urls[:need]
