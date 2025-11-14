import json
from pathlib import Path
from scripts.youtube_uploader import get_youtube_service
DATA = Path(__file__).resolve().parent.parent / 'data' / 'performance_data.json'
def fetch_video_stats(video_ids):
    yt = get_youtube_service()
    stats = {}
    if not video_ids:
        return stats
    resp = yt.videos().list(part='statistics,snippet', id=','.join(video_ids)).execute()
    for it in resp.get('items', []):
        vid = it['id']
        stats[vid] = {'views': int(it.get('statistics', {}).get('viewCount', 0)), 'likes': int(it.get('statistics', {}).get('likeCount', 0) if 'likeCount' in it.get('statistics', {}) else 0), 'title': it.get('snippet', {}).get('title', '')}
    return stats
def update_performance_data(new_entries):
    pdata = {}
    if DATA.exists():
        try:
            pdata = json.loads(DATA.read_text())
        except Exception:
            pdata = {}
    video_ids = [e['video_id'] for e in new_entries if e.get('video_id')]
    stats = fetch_video_stats(video_ids)
    for e in new_entries:
        vid = e.get('video_id'); animal = e.get('animal_name')
        if not vid or not animal: continue
        pdata.setdefault(animal, []).append({'video_id': vid, 'views': stats.get(vid, {}).get('views',0)})
    DATA.write_text(json.dumps(pdata, indent=2))
    return pdata
def recommend_top_animals(n=5):
    pdata = {}
    if DATA.exists():
        try:
            pdata = json.loads(DATA.read_text())
        except: pdata = {}
    avg_scores = []
    for animal, records in pdata.items():
        avg = sum(r.get('views',0) for r in records) / max(1,len(records))
        avg_scores.append((animal,avg))
    avg_scores.sort(key=lambda x:x[1], reverse=True)
    return [a for a,s in avg_scores[:n]]
