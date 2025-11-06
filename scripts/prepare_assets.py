# scripts/prepare_assets.py
import os, subprocess, json, time, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
OUT = ROOT / "output"
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

def run_generator():
    rep = ROOT / "scripts" / "generate_cartoon_images_replicate.py"
    gen = ROOT / "scripts" / "generate_images.py"
    ran = False
    if rep.exists():
        try:
            subprocess.run(["python3", str(rep)], check=True, timeout=900)
            ran = True
        except Exception as e:
            print("Replicate script failed:", e)
    if not ran and gen.exists():
        try:
            subprocess.run(["python3", str(gen)], check=True, timeout=900)
            ran = True
        except Exception as e:
            print("generate_images.py failed:", e)
    if not ran:
        print("No generation script ran; will create fallbacks.")

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
    img = Image.new("RGB", (W,H), (200,220,255))
    draw = ImageDraw.Draw(img)
    # simple gradient
    for y in range(H):
        col = (int(200 - y*0.05), int(220 - y*0.08), 255)
        draw.line([(0,y),(W,y)], fill=col)
    draw.ellipse((W-160,40,W-60,140), fill=(255,230,70))
    draw.rectangle((0,H-140,W,H), fill=(180,230,145))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    draw.text((20,20), (hint or f"Scene {idx}")[:140], fill=(10,10,10), font=font)
    out = ASSETS / f"scene{idx}_bg.png"
    img.save(out)
    print("Created fallback", out)

def main():
    run_generator()
    time.sleep(1)
    prompts = load_prompts()
    if not prompts:
        for i in range(1,11):
            if not (ASSETS / f"scene{i}_bg.png").exists():
                create_fallback(i, f"Fallback scene {i}")
        return
    for p in prompts:
        idx = p.get("scene_index")
        path = ASSETS / f"scene{idx}_bg.png"
        if not path.exists():
            create_fallback(idx, p.get("prompt",""))
    print("prepare_assets done. assets list:")
    for f in sorted(ASSETS.glob("scene*_bg.png")):
        print(" -", f)

if __name__ == "__main__":
    main()
