# scripts/generate_images.py
import os, sys, time, requests, json
from pathlib import Path
from PIL import Image
import io
import numpy as np
import cv2

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
OUT = Path("output")
ASSETS = Path("assets")
ASSETS.mkdir(parents=True, exist_ok=True)

def search_pexels(query):
    if not PEXELS_KEY:
        return None
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_KEY}
    params = {"query": query, "per_page": 10}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    photos = data.get("photos", [])
    if not photos:
        return None
    # choose best resolution (original or large2x)
    for ph in photos:
        src = ph.get("src",{})
        url = src.get("large2x") or src.get("large") or src.get("original")
        if url:
            return url
    return None

def download_image(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")

def cartoonize_pil(pil_img):
    # convert to OpenCV
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    # Resize to 1280x720 preserving aspect
    h, w = img.shape[:2]
    target_w, target_h = 1280, 720
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w*scale), int(h*scale)
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    # pad to target size
    top = (target_h - new_h) // 2
    left = (target_w - new_w) // 2
    canvas = np.full((target_h, target_w, 3), 255, dtype=np.uint8)
    canvas[top:top+new_h, left:left+new_w] = img
    img = canvas

    # Cartoon effect: bilateral filter + edge mask
    num_bilateral = 6
    img_color = img.copy()
    for _ in range(num_bilateral):
        img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=75, sigmaSpace=75)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)
    edges = cv2.adaptiveThreshold(img_blur, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, blockSize=9, C=2)

    # convert back to color edges
    edges_col = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    # combine color and edges
    cartoon = cv2.bitwise_and(img_color, edges_col)
    # optional: increase saturation and contrast
    hsv = cv2.cvtColor(cartoon, cv2.COLOR_BGR2HSV).astype("float32")
    hsv[...,1] = hsv[...,1]*1.15
    hsv[...,2] = np.clip(hsv[...,2]*1.05, 0, 255)
    cartoon = cv2.cvtColor(hsv.astype("uint8"), cv2.COLOR_HSV2BGR)

    # convert back to PIL RGB
    pil_out = Image.fromarray(cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB))
    return pil_out

def main():
    prompts_path = OUT / "prompts.json"
    if not prompts_path.exists():
        print("Missing output/prompts.json — run generate_script_and_prompts.py first")
        return
    prompts = json.load(open(prompts_path, encoding="utf-8"))
    for p in prompts:
        idx = p["scene_index"]
        q = p["search_query"]
        print(f"Scene {idx} search: {q}")
        try:
            img_url = search_pexels(q)
            if img_url:
                print("Found Pexels image:", img_url)
                img = download_image(img_url)
            else:
                print("No Pexels results — using placeholder generated image")
                # generate a simple gradient if nothing found
                from PIL import ImageDraw, ImageFont
                img = Image.new("RGB", (1280,720), (200,230,255))
                d = ImageDraw.Draw(img)
                d.text((40,40), q, fill=(10,10,10))
            cartoon = cartoonize_pil(img)
            out_path = ASSETS / f"scene{idx}_bg.png"
            cartoon.save(out_path, "PNG")
            print("Saved cartoonized scene to", out_path)
            time.sleep(1.0)
        except Exception as e:
            print("Error generating scene", idx, e)

if __name__ == "__main__":
    main()
