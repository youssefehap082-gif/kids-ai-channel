# scripts/generate_script.py
# produce a slightly different episode each run (randomized elements)
import json, os, random, time
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

characters = ("Max","Sam","Lily","Alex","Emma")
locations = ("the village square","a small forest","a moonlit hill","the old bridge","a cozy garden")
objects = ("a shiny pebble","a glowing leaf","a tiny map","a twinkling shell","a little compass")
lessons = ("teamwork","kindness","bravery","sharing","honesty")

ep_ts = int(time.time())
seed = ep_ts % 100000
random.seed(seed)

loc = random.choice(locations)
obj = random.choice(objects)
lesson = random.choice(lessons)

title = f"Max & Sam | Episode {ep_ts % 1000}: The Little {obj.split()[1].capitalize()} Map"

script = {
  "title": title,
  "scenes": [
    {
      "time": "0:00",
      "image_prompt": f"cute cartoon two friends (Max and Sam) in {loc}, 2D children's book style, bright colors, morning",
      "dialogue": [
        {"speaker":"Max","text":"Good morning! I'm Max. Today we will look for a little map."},
        {"speaker":"Sam","text":f"Hello Max! I found {obj} — maybe it's a map to something special!"}
      ]
    },
    {
      "time": "1:00",
      "image_prompt": f"cartoon path leading through {loc} with small glowing markers, child-friendly illustration",
      "dialogue": [
        {"speaker":"Max","text":"Follow the glowing markers, step by step."},
        {"speaker":"Sam","text":"Remember, it's easier when we help each other."}
      ]
    },
    {
      "time": "2:00",
      "image_prompt": "friendly cartoon owl pointing at a map under the stars, whimsical style",
      "dialogue": [
        {"speaker":"Owl","text":f"Hoo-hoo! This story teaches {lesson}. Use it wisely."},
        {"speaker":"Max","text":"We found something important today."},
        {"speaker":"Sam","text":"Thank you for joining our adventure!"},
        {"speaker":"Narrator","text":"Subscribe, like and hit the bell for the next episode!"}
      ]
    }
  ]
}

with open(os.path.join(OUT_DIR, "script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

print("Wrote", os.path.join(OUT_DIR, "script.json"))
print("Episode title:", title)
