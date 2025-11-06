# scripts/generate_script_and_prompts.py
import json, os, random, time
OUT="output"
os.makedirs(OUT, exist_ok=True)
ts = int(time.time()) % 100000
title = f"Max & Sam | Episode {ts}: Little Star Journey"

characters = ["Max","Sam","Lily","Alex","Emma"]
# build 5 scenes with longer dialogues (so audio will be longer)
scenes = []
scenes.append({
  "image_prompt":"orange cat cooking food in simple cozy kitchen, warm light, cinematic",
  "dialogue":[
    {"speaker":"Max","text":"One morning Max woke up with a big idea. He wanted to prepare food for those in need."},
    {"speaker":"Sam","text":"That's wonderful! Let's cook together and share with our friends."},
    {"speaker":"Max","text":"We will start now — step by step, we cook and pack."}
  ]
})
scenes.append({
  "image_prompt":"cat carrying a bowl walking through a small village street, golden hour, heartwarming",
  "dialogue":[
    {"speaker":"Max","text":"Max carried the warm bowl down the lane, greeting everyone with a smile."},
    {"speaker":"Sam","text":"People waved and the children followed, curious and happy."}
  ]
})
scenes.append({
  "image_prompt":"group of stray cats approaching, tension, but friendly resolution, cinematic",
  "dialogue":[
    {"speaker":"Max","text":"Some stray cats approached and seemed upset, but Max offered a plate."},
    {"speaker":"Sam","text":"Sharing calmed them; soon they all sat together to eat."}
  ]
})
scenes.append({
  "image_prompt":"celebration in the village, kids and cats eating together, warm scene",
  "dialogue":[
    {"speaker":"Max","text":"The village gathered and the food was shared. Smiles were everywhere."},
    {"speaker":"Sam","text":"This made Max very happy — helping felt great."}
  ]
})
scenes.append({
  "image_prompt":"sunset scene, Max and Sam waving goodbye, hopeful mood, cinematic",
  "dialogue":[
    {"speaker":"Narrator","text":"And so Max and Sam learned that kindness brings people together. Subscribe for more adventures!"}
  ]
})

script = {"title":title, "scenes":scenes}
with open(os.path.join(OUT,"script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

# create prompts.json (search queries for Pexels)
prompts = []
for i, sc in enumerate(scenes, start=1):
    p = sc.get("image_prompt","cute cat scene")
    # simplify prompt into search-friendly keywords
    search_query = p
    prompts.append({"scene_index":i, "search_query":search_query})
with open(os.path.join(OUT,"prompts.json"), "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print("Wrote output/script.json and output/prompts.json")
