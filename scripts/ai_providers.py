# scripts/ai_optimizer.py
"""
Simple performance-based recommender (starter):
- reads data/performance_data.json
- returns top N animals to repeat
"""
import json
from pathlib import Path
DATA = Path(__file__).resolve().parents[1] / "data"
PERF = DATA / "performance_data.json"

def recommend_top(n=3):
    if not PERF.exists():
        return []
    d = json.loads(PERF.read_text())
    # expect structure: {animal: {views: int, likes:int}}
    scored = []
    for k,v in d.items():
        score = v.get("views",0) + 3 * v.get("likes",0)
        scored.append((score, k))
    scored.sort(reverse=True)
    return [k for s,k in scored[:n]]
