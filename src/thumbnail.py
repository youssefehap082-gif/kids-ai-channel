from PIL import Image, ImageDraw, ImageFont
import requests, os, random

def make_thumbnail(animal_name: str) -> str:
    """
    Generate a simple thumbnail image with the animal name.
    """
    print(f"🖼️ Creating thumbnail for {animal_name}")
    colors = [(255,165,0), (30,144,255), (255,69,0), (34,139,34)]
    bg_color = random.choice(colors)
    img = Image.new('RGB', (1280, 720), bg_color)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
    text = animal_name.upper()
    w, h = draw.textbbox((0, 0), text, font=font)[2:]
    draw.text(((1280 - w) / 2, (720 - h) / 2), text, fill="white", font=font)

    path = f"/tmp/{animal_name.replace(' ', '_')}_thumb.jpg"
    img.save(path)
    return path
