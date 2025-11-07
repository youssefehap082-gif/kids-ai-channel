# scripts/download_stock_videos.py
import os, requests, json, sys, time
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

def try_search_and_download(query, outpath, attempts=3):
    params = {"query": query, "per_page": 15, "size": "medium"}
    for a in range(attempts):
        try:
            r = requests.get(search_url, headers=headers, params=params, timeout=30)
            if r.status_code != 200:
                print(f"Pexels API error {r.status_code}: {r.text}")
                time.sleep(1)
                continue
            data = r.json()
            videos = data.get("videos", [])
            if not videos:
                print("No videos for query:", query)
                return False
            chosen = None
            for v in videos:
                files = v.get("video_files", [])
                for f in files:
                    if f.get("file_type")=="video/mp4" and f.get("quality") in ("hd","sd"):
                        chosen = f
                        break
                if chosen:
                    break
            if not chosen:
                chosen = videos[0]["video_files"][0]
            url = chosen.get("link")
            print("Downloading:", url)
            with requests.get(url, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                with open(outpath, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            fh.write(chunk)
            return True
        except Exception as e:
            print("Download attempt error:", e)
            time.sleep(1)
    return False

generic_fallbacks = ["cute animals", "wildlife close up", "animal close up"]

for s in scenes:
    q = s.get("query","animal")
    idx = s.get("idx")
    outpath = CLIPS / f"clip{idx}.mp4"
    print(f"Scene {idx}: searching for '{q}'")
    ok = try_search_and_download(q, outpath, attempts=2)
    if not ok:
        alt_queries = [
            q + " close up",
            q.split()[0] if " " in q else q
        ]
        found = False
        for aq in alt_queries + generic_fallbacks:
            print("Trying alternative query:", aq)
            if try_search_and_download(aq, outpath, attempts=2):
                found = True
                break
        if not found:
            print("Could not download clip for scene", idx, "- skipping.")
    time.sleep(0.6)
