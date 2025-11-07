# scripts/prepare_assets.py
import os, subprocess, json, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
OUT = ROOT / "output"
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

def run_generator():
    rep = ROOT / "scripts" / "generate_images_replicate.py"
    if rep.exists():
        try:
            subprocess.run(["python3", str(rep)], check=True, timeout=900)
            return
        except Exception as e:
            print("Replicate script failed:", e)
    print("No successful image generation run — creating fallback images.")

def load_prompts():
    p = OUT / "prompts.json"
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print("Error reading prompts.json:", e)
        return []

def create_fallback(idx, hint=""):
    W, H = 1280, 720
    img = Image.new("RGB", (W,H), (255,255,255))
    draw = ImageDraw.Draw(img)
    # draw simple cartoon circle characters and title
    draw.rectangle((60,60,W-60,H-140), outline=(0,0,0), width=3)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font = ImageFont.load_default()
    draw.text((80,80), f"Scene {idx}", fill=(0,0,0), font=font)
    draw.ellipse((120,180,320,380), outline=(0,0,0), width=3)
    out = ASSETS / f"scene{idx}_bg.png"
    img.save(out)
    print("Created fallback", out)

def main():
    run_generator()
    time.sleep(1)
    prompts = load_prompts()
    if not prompts:
        for i in range(1,7):
            create_fallback(i, f"Scene {i}")
        return
    for p in prompts:
        idx = p.get("scene_index")
        path = ASSETS / f"scene{idx}_bg.png"
        if not path.exists():
            create_fallback(idx, p.get("prompt",""))
    print("prepare_assets done.")

if __name__ == "__main__":
    main()
