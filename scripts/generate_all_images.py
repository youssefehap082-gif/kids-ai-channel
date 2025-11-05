# scripts/generate_all_images.py
import os, json, base64, requests
from pathlib import Path
from PIL import Image

HF_TOKEN = os.environ.get("HF_API_TOKEN", "").strip()
HF_MODEL = "prompthero/openjourney-v4"
HF_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

OUT = Path("output")
ASSETS = Path("assets")
ASSETS.mkdir(parents=True, exist_ok=True)

# load script
script = json.load(open(OUT/"script.json", encoding="utf-8"))

def save_bytes(path, b):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b)
    print("Saved", path)

def hf_generate(prompt):
    if not HF_TOKEN:
        return None
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        r = requests.post(HF_URL, headers=headers, json={"inputs": prompt}, timeout=120)
        r.raise_for_status()
        # if direct image
        if r.headers.get("content-type","").startswith("image/"):
            return r.content
        data = r.json()
        if isinstance(data, list) and "generated_image" in data[0]:
            return base64.b64decode(data[0]["generated_image"])
        return None
    except Exception as e:
        print("HF gen failed:", e)
        return None

# CHARACTER ASSETS: generate one PNG per character (transparent background) and mouths
characters = set()
for sc in script["scenes"]:
    for d in sc["dialogue"]:
        characters.add(d["speaker"])
characters = sorted(list(characters))
print("Characters:", characters)

# create or reuse character images
for ch in characters:
    # normalize names for filenames
    key = ch.replace(" ", "_")
    char_path = ASSETS/f"{key}.png"
    if not char_path.exists():
        prompt = f"Cartoon character portrait of {ch}, child-friendly, vector-like, PNG transparent background, head-and-shoulders, 2D"
        img_bytes = hf_generate(prompt)
        if img_bytes:
            save_bytes(char_path, img_bytes)
        else:
            # draw simple face placeholder with Pillow
            from PIL import Image, ImageDraw, ImageFont
            W,H = 400,400
            img = Image.new("RGBA",(W,H),(0,0,0,0))
            draw = ImageDraw.Draw(img)
            # head circle
            draw.ellipse((50,40,350,340), fill=(255,225,200,255), outline=(0,0,0))
            # eyes
            draw.ellipse((140,150,170,180), fill=(0,0,0))
            draw.ellipse((230,150,260,180), fill=(0,0,0))
            # mouth placeholder (will be replaced by mouth overlays later)
            draw.arc((160,210,240,260), start=200, end=340, fill=(0,0,0), width=4)
            # label
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            except:
                font = ImageFont.load_default()
            draw.text((10,10), ch, fill=(0,0,0), font=font)
            img.save(char_path)
            print("Saved placeholder character", char_path)

    # create mouth frames if not exists (closed, mid, open)
    for mouth in ("mouth_closed","mouth_mid","mouth_open"):
        mouth_path = ASSETS/f"{key}_{mouth}.png"
        if not mouth_path.exists():
            # attempt HF
            prompt = f"PNG image of a cartoon {ch} mouth: {mouth} (transparent background), simple vector style"
            img_bytes = hf_generate(prompt)
            if img_bytes:
                save_bytes(mouth_path, img_bytes)
            else:
                # draw simple mouth shape
                from PIL import Image, ImageDraw
                W,H = 200,100
                img = Image.new("RGBA",(W,H),(0,0,0,0))
                draw = ImageDraw.Draw(img)
                if mouth=="mouth_closed":
                    draw.rectangle((20,40,180,60), fill=(150,30,30))
                elif mouth=="mouth_mid":
                    draw.ellipse((20,30,180,70), fill=(150,30,30))
                else:
                    draw.ellipse((10,20,190,80), fill=(150,30,30))
                img.save(mouth_path)
                print("Saved placeholder mouth", mouth_path)

# BACKGROUNDS: one per scene
for idx, sc in enumerate(script["scenes"], start=1):
    bg_path = ASSETS/f"scene{idx}_bg.png"
    if not bg_path.exists():
        prompt = sc.get("image_prompt","cartoon background, 1280x720, kid friendly")
        bytes_img = hf_generate(prompt)
        if bytes_img:
            save_bytes(bg_path, bytes_img)
        else:
            # draw simple gradient background
            from PIL import Image, ImageDraw, ImageFont
            W,H = 1280,720
            img = Image.new("RGB",(W,H),(160,220,255))
            draw = ImageDraw.Draw(img)
            # ground
            draw.rectangle((0,H-140,W,H), fill=(180,230,150))
            # sun
            draw.ellipse((W-140,40,W-40,140), fill=(255,220,70))
            # small hill
            draw.ellipse((-200,380,600,900), fill=(150,200,120))
            img.save(bg_path)
            print("Saved placeholder bg", bg_path)

print("Image generation done. Assets in assets/")
