# scripts/generate_thumbnail.py
import os, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
OUT = Path("output")
TH = Path("thumbnails")
TH.mkdir(parents=True, exist_ok=True)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# pick the main produced file (info prioritized)
candidates = list(OUT.glob("final_*")) + list(OUT.glob("ambient_*"))
for vid in candidates:
    name = vid.stem
    thumb_path = TH / f"{name}.jpg"
    tmp_frame = OUT / f"{name}_thumb_frame.jpg"
    try:
        subprocess.run(["ffmpeg","-y","-ss","3","-i", str(vid), "-frames:v","1", str(tmp_frame)], check=True)
        img = Image.open(tmp_frame).convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(font_path, 48)
        except:
            font = ImageFont.load_default()
        rect_h = 140
        draw.rectangle([(0,H-rect_h),(W,H)], fill=(0,0,0,200))
        # make title more friendly
        title = name.replace("_", " ").replace("final ", "").title()
        draw.text((20, H-rect_h+20), title, fill=(255,255,255), font=font)
        img.save(thumb_path, quality=85)
        tmp_frame.unlink(missing_ok=True)
        print("Created thumbnail", thumb_path)
    except Exception as e:
        print("Thumbnail creation error for", vid, e)
        try:
            tmp_frame.unlink(missing_ok=True)
        except:
            pass
