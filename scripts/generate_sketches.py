# scripts/generate_sketches.py
import cv2, os, json
from pathlib import Path
OUT = Path("output")
ASSETS = Path("assets")
ASSETS.mkdir(parents=True, exist_ok=True)

pfile = OUT / "prompts.json"
if pfile.exists():
    prompts = json.load(open(pfile, encoding="utf-8"))
    count = max([p.get("scene_index",0) for p in prompts], default=6)
else:
    count = 6

for i in range(1, count+1):
    src = ASSETS / f"scene{i}_bg.png"
    dst = ASSETS / f"scene{i}_sketch.png"
    if not src.exists():
        print("Missing source", src, "- skipping")
        continue
    try:
        img = cv2.imread(str(src))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        # invert and soften for marker look
        sketch = cv2.bitwise_not(edges)
        # make background slightly off-white
        h,w = sketch.shape[:2]
        canvas = 255 - sketch  # background is white where sketch==0
        sketch_rgb = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        cv2.imwrite(str(dst), sketch_rgb)
        print("Saved sketch", dst)
    except Exception as e:
        print("Sketch error for", i, e)
