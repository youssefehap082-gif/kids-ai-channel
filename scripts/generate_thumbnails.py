# scripts/generate_thumbnails.py
import os, glob, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("output")
THUMBS = Path("thumbnails")
THUMBS.mkdir(parents=True, exist_ok=True)

# find generated videos (info + ambient)
videos = sorted(OUT.glob("final_*.mp4")) + sorted(OUT.glob("ambient_*.mp4"))
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

for vid in videos:
    name = vid.stem
    thumb_path = THUMBS / f"{name}.jpg"
    # extract frame at 3s
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
        # overlay a semi-transparent rectangle
        rect_h = 120
        draw.rectangle([(0,H-rect_h),(W,H)], fill=(0,0,0,180))
        # write title (use filename nice formatting)
        title = name.replace("_", " ").replace("final ", "").title()
        draw.text((20, H-rect_h+20), title, fill=(255,255,255), font=font)
        img.save(thumb_path, quality=85)
        tmp_frame.unlink(missing_ok=True)
        print("Created thumbnail", thumb_path)
    except Exception as e:
        print("Thumbnail error for", vid, e)
        try:
            tmp_frame.unlink(missing_ok=True)
        except:
            pass
