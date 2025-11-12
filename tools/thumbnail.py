# tools/thumbnail.py
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import requests
from io import BytesIO
import os

def generate_thumbnail(animal, image_url, out_path="thumb.jpg"):
    # image_url can be a file path or URL
    if Path(image_url).exists():
        img = Image.open(image_url).convert("RGB")
    else:
        r = requests.get(image_url, timeout=30)
        img = Image.open(BytesIO(r.content)).convert("RGB")
    img = img.resize((1280,720))
    draw = ImageDraw.Draw(img)
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 90)
    except:
        font = ImageFont.load_default()
    text = animal.upper()
    w,h = draw.textsize(text, font=font)
    # place text bottom-left with stroke
    x, y = 50, 600
    # stroke
    draw.text((x-2,y-2), text, font=font, fill="black")
    draw.text((x+2,y-2), text, font=font, fill="black")
    draw.text((x-2,y+2), text, font=font, fill="black")
    draw.text((x+2,y+2), text, font=font, fill="black")
    draw.text((x,y), text, font=font, fill="yellow")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG")
    return out_path
