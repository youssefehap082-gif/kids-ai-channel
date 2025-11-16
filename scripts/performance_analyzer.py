# scripts/performance_analyzer.py
"""
Minimal analyzer that fetches video stats from YouTube and stores them.
You can run this periodically (separate workflow) to update performance_data.json
"""
import logging
from pathlib import Path
import json
from scripts.youtube_uploader import get_youtube_service

log = logging.getLogger("performance")
DATA = Path(__file__).resolve().parents[1] / "data"
PERF = DATA / "performance_data.json"
PERF.write_text(PERF.read_text() if PERF.exists() else "{}")

def update_stats(video_ids_map):
    """
    video_ids_map: {animal_name: video_id}
    """
    youtube = get_youtube_service()
    out = {}
    for animal, vid in video_ids_map.items():
        try:
            res = youtube.videos().list(part="statistics", id=vid).execute()
            items = res.get("items",[])
            if items:
                stats = items[0].get("statistics",{})
                out[animal] = {"views": int(stats.get("viewCount",0)), "likes": int(stats.get("likeCount",0))}
        except Exception as e:
            log.warning("Failed stats for %s: %s", vid, e)
    PERF.write_text(json.dumps(out, indent=2))
    return out
