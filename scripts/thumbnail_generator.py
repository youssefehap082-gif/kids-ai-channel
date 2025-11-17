"""
scripts/thumbnail_generator.py
Generates N thumbnail variants (HTML + rendering or PIL), ranks them with simple heuristic.
"""
import os
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail_variants(base_image_path: str, title_text: str, out_dir="/tmp/thumbs", variants=4):
    os.makedirs(out_dir, exist_ok=True)
    outputs = []
    for i in range(variants):
        out = os.path.join(out_dir, f"thumb_v{i}.jpg")
        # placeholder: create a simple image with text
        im = Image.new("RGB", (1280,720), color=(255,200 - i*20, 100 + i*30))
        draw = ImageDraw.Draw(im)
        draw.text((50,50), title_text[:60], fill=(255,255,255))
        im.save(out, quality=85)
        outputs.append(out)
    return outputs

def predict_best_thumbnail(paths):
    # simple heuristic: largest filesize (placeholder)
    best = max(paths, key=lambda p: os.path.getsize(p) if os.path.exists(p) else 0)
    return best
