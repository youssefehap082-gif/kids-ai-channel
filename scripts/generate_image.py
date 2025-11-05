# scripts/generate_image.py
# يولّد صور كرتونية باستخدام نموذج متاح على Hugging Face.
# لو فشل النموذج، يولّد صورة افتراضية (Placeholder) بدل ما يفشل السكربت.

import os, requests, sys, base64

HF_TOKEN = os.environ.get("HF_API_TOKEN")
# موديل مجاني مفتوح ويعمل حاليًا
MODEL = "prompthero/openjourney-v4"  # بديل لـ stable-diffusion
URL = f"https://api-inference.huggingface.co/models/{MODEL}"

headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
prompt = sys.argv[1] if len(sys.argv) > 1 else "cute cartoon scene for children"
output_file = sys.argv[2] if len(sys.argv) > 2 else "output/image.png"

os.makedirs(os.path.dirname(output_file), exist_ok=True)

def save_image_from_b64(b64data, path):
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64data))
    print("✅ Image saved to", path)

def fallback_image(path):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (512, 512), color=(255, 230, 200))
    draw = ImageDraw.Draw(img)
    draw.text((20, 230), "Image generation failed", fill=(0, 0, 0))
    img.save(path)
    print("⚠️ Used fallback image:", path)

print(f"🎨 Generating image for prompt: {prompt}")

try:
    payload = {"inputs": prompt}
    response = requests.post(URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict) and "error" in data:
        print("HF error:", data["error"])
        fallback_image(output_file)
    elif isinstance(data, list) and "generated_image" in data[0]:
        save_image_from_b64(data[0]["generated_image"], output_file)
    else:
        # بعض النماذج بترجع الصورة كبايتات مباشرة
        if response.headers.get("content-type", "").startswith("image/"):
            with open(output_file, "wb") as f:
                f.write(response.content)
            print("✅ Direct image saved to", output_file)
        else:
            fallback_image(output_file)
except Exception as e:
    print("❌ Exception while generating image:", e)
    fallback_image(output_file)
