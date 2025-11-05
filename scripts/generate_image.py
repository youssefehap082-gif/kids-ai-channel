# scripts/generate_image.py
import os, sys, requests, base64, subprocess
from PIL import Image, ImageDraw, ImageFont

HF_TOKEN = os.environ.get("HF_API_TOKEN", "")
MODEL = "prompthero/openjourney-v4"
URL = f"https://api-inference.huggingface.co/models/{MODEL}"

def placeholder_with_text(path, prompt):
    # create 1280x720 image with gradient & wrapped prompt text
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), "#A8DDFD")
    draw = ImageDraw.Draw(img)
    # simple gradient
    for i in range(H):
        r = int(168 + (i/H)*60)
        g = int(221 + (i/H)*20)
        b = int(253 - (i/H)*80)
        draw.line([(0,i),(W,i)], fill=(r,g,b))
    # draw a simple star icon
    draw.ellipse((W-180,20,W-80,120), fill=(255,223,70))
    # draw prompt text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()
    margin = 60
    txt = "Prompt: " + prompt
    # wrap text
    lines = []
    words = txt.split()
    line = ""
    for w in words:
        if len(line + " " + w) > 60:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        lines.append(line)
    y = H//2 - 10*len(lines)
    for l in lines:
        draw.text((margin, y), l, fill=(20,30,40), font=font)
        y += 36
    img.save(path, "PNG")
    print("Saved placeholder image to", path)

def save_bytes_image(path, content_bytes):
    with open(path, "wb") as f:
        f.write(content_bytes)
    print("Saved image to", path)

def generate_via_hf(prompt, outpath):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    try:
        r = requests.post(URL, headers=headers, json={"inputs": prompt}, timeout=120)
        r.raise_for_status()
        if r.headers.get("content-type","").startswith("image/"):
            save_bytes_image(outpath, r.content)
            return True
        data = r.json()
        if isinstance(data, list) and "generated_image" in data[0]:
            b64 = data[0]["generated_image"]
            save_bytes_image(outpath, base64.b64decode(b64))
            return True
        # unknown response -> fallback
        print("HF returned unknown format; using placeholder.")
        return False
    except Exception as e:
        print("HF image generation failed:", e)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/generate_image.py \"prompt\" output.png")
        sys.exit(1)
    prompt = sys.argv[1]
    out = sys.argv[2]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    ok = False
    if HF_TOKEN:
        ok = generate_via_hf(prompt, out)
    if not ok:
        placeholder_with_text(out, prompt)
