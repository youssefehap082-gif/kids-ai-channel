# scripts/generate_script.py
import os, requests, json, time

HF_TOKEN = os.environ.get("HF_API_TOKEN")
MODEL = "google/flan-t5-small"  # موديل HF مناسب للأوامر؛ غيره لو تحب

PROMPT = """
You are asked to write an episodic children's story in English for a YouTube channel.
Characters: Hazem, Sheh Madwar, Hind, Alaa, Eman (but each episode must include Hazem and Sheh Madwar as main).
Output JSON with fields:
{
  "title": "Episode Title",
  "scenes": [
    {
      "time": "0:00",
      "image_prompt": "Stable Diffusion prompt for scene image",
      "dialogue": [
         {"speaker":"Hazem","text":"..."},
         {"speaker":"Sheh Madwar","text":"..."},
         ...
      ]
    },
    ...
  ]
}
Make roughly 4 scenes for a ~3-6 minute episode. Use simple kid-friendly language. Make dialogues short (1-2 short sentences each). End with a 10s CTA line: "Subscribe for the next episode".
Return only valid JSON.
"""

OUT_DIR = "output"
OUT_FILE = OUT_DIR + "/script.json"
os.makedirs(OUT_DIR, exist_ok=True)

def call_hf(prompt_text):
    if not HF_TOKEN:
        return None
    url = f"https://api-inference.huggingface.co/models/{MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt_text, "options": {"wait_for_model": True}}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        # try parse JSON in response
        try:
            data = r.json()
            # some models return list/dict; try to extract "generated_text"
            if isinstance(data, list) and len(data)>0 and isinstance(data[0], dict):
                # look for keys
                for k in ("generated_text","text","output"):
                    if k in data[0]:
                        return data[0][k]
                return json.dumps(data, ensure_ascii=False)
            elif isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            else:
                # fallback to raw text
                return r.text
        except ValueError:
            return r.text
    except Exception as e:
        print("HF call failed:", e)
        return None

print("Generating script via Hugging Face...")
generated = call_hf(PROMPT)
if generated:
    # try to load JSON from generated text
    try:
        # sometimes model returns extra text; try to find first '{' and parse
        start = generated.find('{')
        if start != -1:
            gen_json = json.loads(generated[start:])
        else:
            gen_json = json.loads(generated)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(gen_json, f, ensure_ascii=False, indent=2)
        print("Saved script to", OUT_FILE)
        raise SystemExit(0)
    except Exception as e:
        print("Could not parse HF output as JSON:", e)
        # fallback below

# Fallback script (guaranteed valid JSON)
fallback = {
  "title": "Hazem & Sheh Madwar - The Little Star Map",
  "scenes": [
    {
      "time": "0:00",
      "image_prompt": "cute cartoon two friends (Hazem and Sheh Madwar) in a peaceful village square, 2D children's book style, bright colors",
      "dialogue": [
        {"speaker":"Hazem","text":"Hi! I'm Hazem. Today we will find a little star."},
        {"speaker":"Sheh Madwar","text":"Hello! I am Sheh Madwar. Let's go on an adventure!"}
      ]
    },
    {
      "time": "1:00",
      "image_prompt": "cute cartoon forest with glowing pebbles, children book illustration",
      "dialogue": [
        {"speaker":"Hazem","text":"Look, a glowing pebble! I wonder where it leads."},
        {"speaker":"Sheh Madwar","text":"Follow me, Hazem! I think it's a map to the stars."}
      ]
    },
    {
      "time": "2:00",
      "image_prompt": "friendly cartoon owl pointing at a map, night sky, colorful",
      "dialogue": [
        {"speaker":"Hazem","text":"Thank you, owl! We learned to help each other."},
        {"speaker":"Sheh Madwar","text":"We did it together. See you for the next map!"}
      ]
    }
  ]
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(fallback, f, ensure_ascii=False, indent=2)
print("Used fallback script and saved to", OUT_FILE)
