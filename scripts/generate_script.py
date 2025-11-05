# scripts/generate_script.py
import os, requests, json
HF_TOKEN = os.environ.get("HF_API_TOKEN")
MODEL = "google/flan-t5-small"
PROMPT = """
You are asked to write an episodic children's story in English for a YouTube channel.
Characters: Hazem, Sheh Madwar, Hind, Alaa, Eman (use Hazem & Sheh Madwar each episode).
Output valid JSON with fields: title, scenes: [{time, image_prompt, dialogue:[{speaker,text}]}].
Make 3 scenes, simple kid-friendly sentences. End with: "Subscribe for the next episode".
"""
OUT = "output/script.json"
os.makedirs("output", exist_ok=True)
def call_hf(prompt):
    if not HF_TOKEN:
        return None
    url = f"https://api-inference.huggingface.co/models/{MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        r = requests.post(url, headers=headers, json={"inputs": prompt, "options":{"wait_for_model":True}}, timeout=120)
        r.raise_for_status()
        txt = r.text
        # try to extract JSON block
        start = txt.find('{')
        if start != -1:
            txt = txt[start:]
        return txt
    except Exception as e:
        print("HF error:", e)
        return None

out = call_hf(PROMPT)
if out:
    try:
        obj = json.loads(out)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        print("Saved script to", OUT)
    except Exception as e:
        print("HF returned non-JSON, using local fallback:", e)

# fallback if no file
if not os.path.exists(OUT):
    fallback = {
      "title": "Hazem & Sheh Madwar - The Little Star Map",
      "scenes": [
        {
          "time": "0:00",
          "image_prompt": "cute cartoon two friends (Hazem and Sheh Madwar) in a peaceful village square, 2D children's book style",
          "dialogue": [
            {"speaker":"Hazem","text":"Hi! I'm Hazem. Let's find a little star."},
            {"speaker":"Sheh Madwar","text":"I'm Sheh Madwar. Let's go!"}
          ]
        },
        {
          "time":"1:00",
          "image_prompt":"forest path with glowing pebbles, children's illustration",
          "dialogue":[
            {"speaker":"Hazem","text":"Follow the glowing pebbles."},
            {"speaker":"Sheh Madwar","text":"We help each other and we are brave."}
          ]
        },
        {
          "time":"2:00",
          "image_prompt":"friendly owl pointing at a map under the stars",
          "dialogue":[
            {"speaker":"Owl","text":"Hoo-hoo! Work together."},
            {"speaker":"Hazem","text":"We found the star's home."},
            {"speaker":"Sheh Madwar","text":"See you next episode!"}
          ]
        }
      ]
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fallback, f, ensure_ascii=False, indent=2)
    print("Saved fallback script to", OUT)
