# scripts/download_stock_videos.py
import os, requests, json, sys
from pathlib import Path

API_KEY = os.environ.get("PEXELS_API_KEY","").strip()
if not API_KEY:
    print("Set PEXELS_API_KEY in environment (GitHub Secret).")
    sys.exit(1)

OUT = Path("output")
CLIPS = Path("clips")
CLIPS.mkdir(parents=True, exist_ok=True)

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json - run generate_script.py first")
    sys.exit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])

headers = {"Authorization": API_KEY}
search_url = "https://api.pexels.com/videos/search"

for s in scenes:
    q = s.get("query")
    idx = s.get("idx")
    params = {"query": q, "per_page": 5, "size": "medium"}
    print("Searching Pexels for:", q)
    r = requests.get(search_url, headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        print("Pexels API error:", r.status_code, r.text)
        continue
    data = r.json()
    videos = data.get("videos", [])
    if not videos:
        print("No videos found for", q)
        continue
    # pick best candidate (first with sd or hd files)
    chosen = None
    for v in videos:
        files = v.get("video_files", [])
        # prefer mp4 with quality >= sd
        for f in files:
            if f.get("file_type")=="video/mp4" and f.get("quality") in ("sd","hd"):
                chosen = f
                break
        if chosen:
            break
    if not chosen:
        chosen = videos[0]["video_files"][0]
    url = chosen.get("link")
    outpath = CLIPS / f"clip{idx}.mp4"
    try:
        print("Downloading", url)
        with requests.get(url, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with open(outpath, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)
        print("Saved", outpath)
    except Exception as e:
        print("Download error", e)
