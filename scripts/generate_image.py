# scripts/generate_image.py
# Try HF image generation; if it fails, draw a simple cute cartoon scene with Pillow
import os, sys, requests, base64
from pathlib import Path

HF_TOKEN = os.environ.get("HF_API_TOKEN", "").strip()
MODEL = "prompthero/openjourney-v4"
URL = f"https://api-inference.huggingface.co/models/{MODEL}"

OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output/scene_fallback.png")
PROMPT = sys.argv[1] if len(sys.argv) > 1 else "cute cartoon scene"

OUT.parent.mkdir(parents=True, exist_ok=True)

def save_bytes_image(path, content):
    with open(path, "wb") as f:
        f.write(content)
    print("Saved image:", path)

def generate_via_hf(prompt, outpath):
    if not HF_TOKEN:
        print("No HF_TOKEN set, skipping HF generation.")
        return False
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": prompt}
        r = requests.post(URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "")
        if ctype.startswith("image/"):
            save_bytes_image(outpath, r.content)
            return True
        data = r.json()
        # check for base64 field
        if isinstance(data, list) and len(data) > 0 and "generated_image" in data[0]:
            b64 = data[0]["generated_image"]
            save_bytes_image(outpath, base64.b64decode(b64))
            return True
        print("HF returned unexpected format.")
        return False
    except Exception as e:
        print("HF generation error:", e)
        return False

def draw_fallback(prompt, outpath):
    # draw a friendly cartoon scene (sky, sun, two simple characters) using Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as e:
        print("Pillow not installed:", e)
        return False

    W, H = 1280, 720
    img = Image.new("RGB", (W, H), "#A8E6FF")
    draw = ImageDraw.Draw(img)

    # sky gradient
    for y in range(H):
        r = int(168 + (y/H) * 40)
        g = int(230 + (y/H) * 10)
        b = int(255 - (y/H) * 40)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # sun
    draw.ellipse((W-150, 50, W-50, 150), fill=(255, 220, 80))

    # ground
    draw.rectangle([0, H-160, W, H], fill=(170, 215, 125))

    # simple character function
    def draw_character(cx, cy, face_color, body_color, label):
        # head
        r = 60
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=face_color, outline=(0,0,0))
        # eyes
        draw.ellipse((cx-25, cy-15, cx-15, cy-5), fill=(0,0,0))
        draw.ellipse((cx+15, cy-15, cx+25, cy-5), fill=(0,0,0))
        # smile
        draw.arc((cx-25, cy-5, cx+25, cy+35), start=200, end=340, fill=(0,0,0), width=3)
        # body
        draw.rectangle((cx-40, cy+60, cx+40, cy+160), fill=body_color, outline=(0,0,0))
        # legs
        draw.rectangle((cx-30, cy+160, cx-5, cy+200), fill=body_color, outline=(0,0,0))
        draw.rectangle((cx+5, cy+160, cx+30, cy+200), fill=body_color, outline=(0,0,0))
        # label
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        except:
            font = ImageFont.load_default()
        draw.text((cx-40, cy+205), label, fill=(20,20,20), font=font)

    # draw two characters: left & right
    draw_character(380, 300, face_color=(255,230,200), body_color=(255,150,150), label="Max")
    draw_character(820, 300, face_color=(255,235,210), body_color=(150,180,255), label="Sam")

    # small star icons
    draw.ellipse((W-200, 30, W-180, 50), fill=(255,240,100))
    for i in range(5):
        x = 200 + i*120
        y = 80 + (i%2)*20
        draw.ellipse((x, y, x+10, y+10), fill=(255,240,100))

    # optional: small caption (no prompt text)
    try:
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font2 = ImageFont.load_default()
    caption = "Max & Sam - Episode"
    draw.text((20, 20), caption, fill=(10,10,10), font=font2)

    img.save(outpath, "PNG")
    print("Saved fallback cartoon image to", outpath)
    return True

# main flow
ok = generate_via_hf(PROMPT, str(OUT))
if not ok:
    print("Using drawn fallback image (Pillow).")
    draw_fallback(PROMPT, str(OUT))
