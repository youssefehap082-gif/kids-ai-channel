"""
scripts/media_fetcher.py
Fetch images / short clips for facts using prioritized providers.
Environment keys: PEXELS_API_KEY, PIXABAY_API_KEY, STORYBLOCKS_API_KEY, VECTEEZY_API_KEY
"""
import os
import logging
from typing import List, Dict
from scripts.utils.http import get

logger = logging.getLogger("kids_ai.media")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

def search_pexels(query: str, per_page=3) -> List[str]:
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        logger.warning("PEXELS_API_KEY not set")
        return []
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": key}
    r = get(url=url, headers=headers, params={"query": query, "per_page": per_page})
    if r.get("json"):
        photos = r["json"].get("photos", [])
        return [p.get("src", {}).get("large") for p in photos if p.get("src")]
    return []

def search_pixabay(query: str, per_page=3) -> List[str]:
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        logger.warning("PIXABAY_API_KEY not set")
        return []
    url = "https://pixabay.com/api/"
    r = get(url=url, params={"key": key, "q": query, "per_page": per_page})
    if r.get("json"):
        hits = r["json"].get("hits", [])
        return [h.get("largeImageURL") for h in hits]
    return []

def fetch_media_for_topic(topic: str, facts: List[str]) -> Dict[int, List[str]]:
    """Return mapping fact_index -> list of media URLs (ordered by priority)"""
    media_map = {}
    for i, fact in enumerate(facts):
        q = f"{topic} {fact.split()[0:3]}"
        urls = search_pexels(topic) or search_pixabay(topic) or []
        media_map[i] = urls or [None]
    return media_map
