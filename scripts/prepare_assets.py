# scripts/prepare_assets.py
# Ensure assets exist: try to run generate_images.py (or replicate script),
# then create fallback cartoon backgrounds if missing.
import os
import subprocess
import json
import time
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(".")
OUT = ROOT / "output"
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

def run_generate_images():
    gen = ROOT / "scripts" / "generate_images.py"
    gen_rep = ROOT / "scripts" / "generate_cartoon_images_replicate.py"
    ran = False
    # Try replicate generator first if exists
    if gen_rep.exists():
        print("Running scripts/generate_cartoon_images_replicate.py ...")
        try:
            subprocess.run(["python3", str(gen_rep)], check=True, timeout=900)
            print("generate_cartoon_images_replicate.py finished.")
            ran = True
        except subprocess.CalledProcessError as e:
            print("generate_cartoon_images_replicate.py returned non-zero:", e)
        except Exception as e:
            print("generate_cartoon_images_replicate.py run error:", e)
    # Fallback to generic generate_images.py (pexels/cartoonize) if exists
    if gen.exists():
        print("Running scripts/generate_images.py ...")
        try:
            subprocess.run(["python3", str(gen)], check=True, timeout=900)
            print("generate_images.py finished.")
            ran = True
        except subprocess.CalledProcessError as e:
            print("generate_images.py returned non-zero:", e)
        except Exception as e:
            print("generate_images.py run error:", e)
    if not ran:
        print("No image-generation script found to run (replicate or pexels). Will create fallbacks.")

def load_prompts():
    p = OUT / "prompts.json"
    if not p.exists():
        print("Missing output/prompts.json — cannot auto-download. Please run generate_script_and_prompts.py first.")
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data
    except Exception as e:
        print("Error reading prompts.json:", e)
        return []

def create_fallback_bg(idx, text_hint=None):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), "#CFE8FF")
    draw = ImageDraw.Draw(img)
    # sky gradient
    for y in range(H):
        r = int(210 - (y/H)*60)
        g = int(235 - (y/H)*80)
        b = int(255 - (y/H)*45)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # sun
    draw.ellipse((W-160,40,W-60,140), fill=(255,230,70))
    # hills
    draw.ellipse((-200,380,700,900), fill=(150,210,120))
    draw.ellipse((500,420,1400,980), fill=(120,190,100))
    # foreground strip
    draw.rectangle((0,H-140,W,H), fill=(180,230,145))
    # two simple characters as circles
    draw.ellipse((200,200,420,420), fill=(255,230,200), outline=(0,0,0))
    draw.ellipse((860,200,1080,420), fill=(255,230,200), outline=(0,0,0))
    # small mouths
    draw.ellipse((300,300,360,330), fill=(160,30,30))
    draw.ellipse((960,300,1020,330), fill=(160,30,30))
    # caption/hint
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    hint = (text_hint or "")[:140]
    draw.text((20,20), hint, fill=(20,20,20), font=font)
    out = ASSETS / f"scene{idx}_bg.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    print("Created fallback cartoon background:", out)

def main():
    # Try to run any image generator script available
    run_generate_images()
    # small pause to allow files to appear
    time.sleep(1)

    prompts = load_prompts()
    if not prompts:
        print("No prompts found. Creating 5 generic fallback backgrounds as safety.")
        for i in range(1,6):
            create_fallback_bg(i, f"Fallback scene {i}")
        return

    # For each prompt, ensure asset exists; if not create fallback
    for p in prompts:
        idx = p.get("scene_index")
        hint = p.get("search_query", "") or p.get("prompt", "")
        path = ASSETS / f"scene{idx}_bg.png"
        if path.exists():
            print("Found existing asset for scene", idx, path)
            continue
        print("Asset missing for scene", idx, "-> creating fallback cartoon image.")
        create_fallback_bg(idx, hint)

    # final report: list assets
    print("Assets folder contents:")
    for f in sorted(ASSETS.glob("scene*_bg.png")):
        print(" -", f)

if __name__ == "__main__":
    main()
