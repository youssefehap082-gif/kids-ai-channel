# scripts/generate_script.py
# يحاول يولد سكربت حلقة من Hugging Face Inference باستخدام نموذج مناسب.
# لو فشل لأي سبب، يولد سكربت افتراضي بسيط لضمان عدم توقف الـ workflow.

import os, requests, json, sys, time

HF_TOKEN = os.environ.get("HF_API_TOKEN")
# موديل متوافق مع Inference API للاوامر
MODEL = "google/flan-t5-small"

prompt = """
Write a children's story episode in English (characters: Hazem and Sheh Madwar).
Length ~6 minutes (about 700-900 words). Output JSON with fields:
{ "title": "...", "scenes": [ {"time":"0:00","voice":"...","image_prompt":"..."} ... ] }
Make it family friendly and end with: "Subscribe for the next episode".
"""

OUT_DIR = "output"
OUT_FILE = os.path.join(OUT_DIR, "script_raw.txt")

os.makedirs(OUT_DIR, exist_ok=True)

def save_text(text):
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print("Saved", OUT_FILE)

def call_hf(model, prompt_text, retries=2):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    payload = {"inputs": prompt_text, "options": {"wait_for_model": True}}
    for attempt in range(retries+1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            # if HF returns non-JSON (e.g., an error page), r.raise_for_status will raise
            r.raise_for_status()
            # some text models return JSON array or text; try decode
            try:
                data = r.json()
                # if it's a list or dict with generated text
                if isinstance(data, (list, dict)):
                    # try to extract generated text fields
                    if isinstance(data, list) and len(data)>0 and "generated_text" in data[0]:
                        return data[0]["generated_text"]
                    # fallback: join repr
                    return json.dumps(data, ensure_ascii=False, indent=2)
            except ValueError:
                # not JSON, return raw text
                return r.text
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None

print("Calling Hugging Face model:", MODEL)
generated = None
if HF_TOKEN:
    generated = call_hf(MODEL, prompt, retries=2)
else:
    print("Warning: HF_API_TOKEN not set. Will use fallback script.")

if generated:
    save_text(generated)
else:
    # Fallback: create a simple JSON script so the pipeline يمكنه المتابعة
    fallback = {
        "title": "Hazem & Sheh Madwar - The Little Star Map",
        "scenes": [
            {"time": "0:00", "voice": "Hello! I am Hazem. Today Sheh Madwar and I will find a little star map.", "image_prompt": "cute cartoon two friends exploring a night forest, 2D children's book style"},
            {"time": "0:40", "voice": "They walk and find a glowing pebble that points to the sky.", "image_prompt": "cartoon glowing pebble in a forest clearing, children book style"},
            {"time": "1:20", "voice": "A friendly owl helps them read the map and they sing a little song.", "image_prompt": "friendly cartoon owl showing a map to two kids, bright colors"},
            {"time": "2:00", "voice": "They follow the map and learn to help each other. The end.", "image_prompt": "two friends hugging under a moonlit sky, cute illustration"}
        ],
        "note": "This is a fallback script generated locally because HF API failed."
    }
    text = json.dumps(fallback, ensure_ascii=False, indent=2)
    save_text(text)
    print("Used fallback script (local) to avoid workflow failure.")
