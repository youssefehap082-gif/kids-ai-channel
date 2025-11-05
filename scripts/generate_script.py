# scripts/generate_script.py
import json, os, time, random

OUT = "output"
os.makedirs(OUT, exist_ok=True)

characters = ["Max","Sam","Lily","Alex","Emma"]
# We'll keep main pair Max & Sam always present
ep_id = int(time.time()) % 100000
title = f"Max & Sam | Episode {ep_id}: The Little Star Map"

# create 5-6 scenes with multiple short lines so audio length increases
scenes = []
locations = ["the village square","a small forest","the moonlit hill","the old bridge","a cozy garden"]
objects = ["a shiny pebble","a tiny map","a glowing shell","a twinkling compass","a little star"]

for i in range(1,6):
    loc = random.choice(locations)
    obj = random.choice(objects)
    prompt = f"cute cartoon background: {loc}, 2D children's book illustration, bright colors, wide scene, simple characters space for overlay"
    # build dialogue: 3-5 lines
    dialogue = []
    # always start with Max & Sam
    dialogue.append({"speaker":"Max","text":f"Look, Sam! I found {obj} near {loc}."})
    dialogue.append({"speaker":"Sam","text":"Wow! Maybe it will lead us to something special."})
    # add a supporting friend occasionally
    if random.random() < 0.5:
        friend = random.choice(["Lily","Alex","Emma"])
        dialogue.append({"speaker":friend,"text":"Be careful, follow the glowing path together."})
    dialogue.append({"speaker":"Max","text":"Let's work together and see where it goes."})
    dialogue.append({"speaker":"Sam","text":"Yes — teamwork will help us!"})
    if i == 5:
        dialogue.append({"speaker":"Narrator","text":"Don't forget to subscribe, like and hit the bell for the next episode!"})
    scenes.append({"time":f"0:0{i-1}","image_prompt":prompt,"dialogue":dialogue})

script = {"title": title, "scenes": scenes}
with open(os.path.join(OUT, "script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

print("Wrote", os.path.join(OUT, "script.json"))
print("Title:", title)
