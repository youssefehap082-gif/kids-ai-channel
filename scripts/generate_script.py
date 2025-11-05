# scripts/generate_script.py
import json, os
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

script = {
  "title": "Max & Sam | Episode 1: The Little Star Map",
  "scenes": [
    {
      "time": "0:00",
      "image_prompt": "cute cartoon two friends (Max and Sam) in a peaceful village square, 2D children's book style, bright colors, morning",
      "dialogue": [
        {"speaker":"Max","text":"Good morning! I'm Max. Today we will look for a little star map."},
        {"speaker":"Sam","text":"Hello Max! I found a shiny pebble — maybe it's a map to the stars!"}
      ]
    },
    {
      "time": "1:00",
      "image_prompt": "cartoon small forest path with glowing pebbles leading the way, child-friendly illustration",
      "dialogue": [
        {"speaker":"Max","text":"Look! The pebble lights up when we step — follow me."},
        {"speaker":"Sam","text":"We must be brave together."}
      ]
    },
    {
      "time": "2:00",
      "image_prompt": "friendly cartoon owl on a branch showing a map under the moonlight, whimsical style",
      "dialogue": [
        {"speaker":"Owl","text":"Hoo-hoo! The little map needs teamwork. Share and help each other."},
        {"speaker":"Max","text":"We helped the lost star find its home."},
        {"speaker":"Sam","text":"Thank you for joining us. See you next time!"},
        {"speaker":"Narrator","text":"Don't forget to subscribe, like and enable the bell to never miss a new episode!"}
      ]
    }
  ]
}

with open(os.path.join(OUT_DIR, "script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)
print("Wrote output/script.json (Episode 1 template).")
