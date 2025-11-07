# scripts/download_stock_videos.py
import os, requests, json, sys
from pathlib import Path
OUT = Path("output")
CLIPS = Path("clips")
CLIPS.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("PEXELS_API_KEY","").strip()
if not API_KEY:
    print("Set PEXELS_API_KEY in environment (GitHub Secret).")
    sys.exit(1)

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json - run generate_script_animal.py first")
    sys.exit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])

headers = {"Authorization": API_KEY}
search_url = "https://api.pexels.com/videos/search"

for s in scenes:
    q = s.get("query","animal")
    idx = s.get("idx")
    params = {"query": q, "per_page": 8, "size": "medium"}
    print(f"Searching Pexels for scene {idx}: {q}")
    try:
        r = requests.get(search_url, headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            print("Pexels API error:", r.status_code, r.text)
            continue
        data = r.json()
        videos = data.get("videos", [])
        if not videos:
            print("No videos found for", q)
            continue
        # pick best candidate (prefer hd)
        chosen = None
        for v in videos:
            files = v.get("video_files", [])
            # prefer mp4 with quality hd or sd
            for f in files:
                if f.get("file_type")=="video/mp4" and f.get("quality") in ("hd","sd"):
                    chosen = f
                    break
            if chosen:
                break
        if not chosen:
            chosen = videos[0]["video_files"][0]
        url = chosen.get("link")
        outpath = CLIPS / f"clip{idx}.mp4"
        print("Downloading", url)
        with requests.get(url, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with open(outpath, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)
        print("Saved", outpath)
    except Exception as e:
        print("Error for scene", idx, e)
