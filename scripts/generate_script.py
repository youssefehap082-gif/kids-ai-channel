# scripts/generate_script.py
import json, time, random, os
OUT = "output"
os.makedirs(OUT, exist_ok=True)

# قالب عناوين يمكن تغييره أو زيادة القوائم
themes = [
  "cute cat playing with toy",
  "funny cat fails",
  "adorable kitten sleeping",
  "funny dog playing",
  "puppy meets baby",
  "cat vs box",
  "dog rescues kitten",
  "cat reaction to cucumber",
  "panda eating bamboo",
  "squirrel eating nut"
]

# pick 3 clips per short (15-45s final)
num_clips = 3
chosen = random.sample(themes, k=num_clips)

scenes = []
for i,q in enumerate(chosen, start=1):
    # create a short caption line for the clip
    caption_templates = [
        "Look at this little one! 🥰",
        "Too cute to handle! 😍",
        "Wait for the reaction... 😂",
        "Who else wants a pet like this? 🐾",
        "Absolute mood booster! ✨"
    ]
    caption = random.choice(caption_templates)
    # optionally add query modifiers for Pexels (english)
    query = q + " cute baby animal"
    scenes.append({"idx": i, "query": query, "caption": caption})

title = f"Cute Animals Daily #{int(time.time())%100000}"
script = {"title": title, "scenes": scenes}
with open(os.path.join(OUT,"script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

print("Wrote", OUT+"/script.json")
print(json.dumps(script, indent=2))
