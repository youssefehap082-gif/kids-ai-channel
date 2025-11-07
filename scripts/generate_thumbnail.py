#!/usr/bin/env python3
# scripts/generate_thumbnail.py
import os, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
OUT = Path("output")
TH = Path("thumbnails")
TH.mkdir(parents=True, exist_ok=True)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
candidates = list(OUT.glob("final_*.mp4")) + list(OUT.glob("ambient_*.mp4"))
for vid in candidates:
    try:
        tmp = OUT / f"{vid.stem}_frame.jpg"
        subprocess.run(["ffmpeg","-y","-ss","3","-i", str(vid), "-frames:v","1", str(tmp)], check=True)
        img = Image.open(tmp).convert("RGB")
        W,H = img.size
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(font_path, 48)
        except:
            font = ImageFont.load_default()
        draw.rectangle([(0,H-140),(W,H)], fill=(0,0,0,200))
        title = vid.stem.replace("_"," ").title()
        draw.text((20,H-120), title, fill=(255,255,255), font=font)
        outp = TH / f"{vid.stem}.jpg"
        img.save(outp, quality=85)
        tmp.unlink(missing_ok=True)
        print("Thumbnail created:", outp.name)
    except Exception as e:
        print("Thumbnail error for", vid.name, e)
