
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def generate_thumbnail(animal, image_url, out_path):
    r = requests.get(image_url, timeout=30)
    img = Image.open(BytesIO(r.content)).convert("RGB")
    img = img.resize((1280, 720))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    draw.text((50, 600), animal.upper(), fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    img.save(out_path, "JPEG")
    return out_path

