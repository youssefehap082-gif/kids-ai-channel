#!/usr/bin/env python3
# scripts/generate_script_facts.py
import os, json, random
OUT = "output"
STATE_DIR = "state"
STATE_FILE = os.path.join(STATE_DIR, "state.json")
os.makedirs(OUT, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

# قاعدة بسيطة: أضف حيوانات أكثر حسب رغبتك
FACTS_DB = {
    "panda": {
        "name": "Giant Panda",
        "queries": ["panda", "giant panda", "panda cub playing", "panda eating bamboo"],
        "facts": [
            "Pandas live mainly in bamboo forests in China.",
            "Pandas spend up to 14 hours a day eating bamboo.",
            "An adult panda can eat roughly 20 to 40 kilograms of bamboo daily.",
            "Baby pandas are born blind and tiny compared to their mothers.",
            "Pandas have a pseudo-thumb to help hold bamboo while eating.",
            "Pandas are mostly solitary animals and mark territory with scent.",
            "Their black and white fur helps camouflage them in snow and forests.",
            "Pandas can climb trees and are good swimmers.",
            "Conservation efforts helped panda numbers slowly recover.",
            "Pandas communicate using vocal sounds and scent markings."
        ]
    },
    "giraffe": {
        "name": "Giraffe",
        "queries": ["giraffe", "giraffe eating leaves", "baby giraffe"],
        "facts": [
            "Giraffes are the tallest land animals.",
            "A giraffe's neck can reach up to 2 meters long.",
            "They have a long prehensile tongue up to 45 cm.",
            "Each giraffe's spot pattern is unique like fingerprints.",
            "They live in groups called towers.",
            "Giraffes have powerful hearts to pump blood up the neck.",
            "Calves can stand and run within hours of birth.",
            "Giraffes sleep very little and often standing up.",
            "They drink water infrequently and can go days without it.",
            "Males fight by swinging their necks in a behavior called necking."
        ]
    },
    "elephant": {
        "name": "African Elephant",
        "queries": ["elephant", "elephant herd", "elephant baby"],
        "facts": [
            "Elephants are the largest land animals on Earth.",
            "They have long trunks used for breathing, grasping and drinking.",
            "Elephants are highly social and live in family groups.",
            "They use infrasound to communicate over long distances.",
            "Elephants have strong memory and complex emotions.",
            "They can drink up to 200 liters of water a day.",
            "Calves are cared for by the entire herd, not just the mother.",
            "Elephants help shape ecosystems by creating waterholes.",
            "Their tusks are elongated incisors made of ivory.",
            "Human activities pose major threats to elephant populations."
        ]
    }
}

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            return json.load(open(STATE_FILE, encoding="utf-8"))
    except:
        pass
    return {}

def save_state(s):
    json.dump(s, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

state = load_state()
recent = state.get("recent", [])

choices = list(FACTS_DB.keys())
random.shuffle(choices)
# pick next animal not recently used
animal_key = None
for c in choices:
    if c not in recent:
        animal_key = c
        break
if not animal_key:
    animal_key = choices[0]

data = FACTS_DB[animal_key]
title = f"10 Amazing Facts About {data['name']}"
scenes = []
for idx, fact in enumerate(data["facts"][:10], start=1):
    scenes.append({
        "idx": idx,
        "headline": f"Fact {idx}",
        "text": fact,
        "query": random.choice(data["queries"])
    })

script = {
    "title": title,
    "description": f"{title}\nClips source: Pexels / Pixabay (royalty-free).",
    "tags": [data["name"].split()[0].lower(), "animal facts", "wildlife", "fun facts"],
    "animal_key": animal_key,
    "scenes": scenes
}

open(os.path.join(OUT, "script.json"), "w", encoding="utf-8").write(json.dumps(script, ensure_ascii=False, indent=2))
print("WROTE output/script.json for", data["name"])

recent.insert(0, animal_key)
recent = recent[:50]
state["recent"] = recent
save_state(state)
print("Updated state:", recent)
