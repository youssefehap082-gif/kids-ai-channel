#!/usr/bin/env python3
# scripts/generate_script_facts.py
# Generate a script with 10 facts for a chosen animal (default: panda).
import os, json, random
OUT = "output"
STATE_DIR = "state"
STATE_FILE = os.path.join(STATE_DIR, "state.json")
os.makedirs(OUT, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

# DB of animals (expandable)
FACTS_DB = {
    "panda": {
        "name": "Giant Panda",
        "queries": ["panda eating bamboo", "panda cub playing", "giant panda forest"],
        "facts": [
            "Pandas live mainly in bamboo forests in China.",
            "Pandas spend up to 14 hours a day eating bamboo.",
            "An adult panda can eat roughly 20-40 kg of bamboo daily.",
            "Baby pandas are born very tiny and blind.",
            "Pandas have a pseudo-thumb to help hold bamboo.",
            "Pandas are solitary animals and communicate by scent.",
            "Their fur pattern helps with camouflage and signaling.",
            "Pandas have a strong sense of smell to find mates and territory.",
            "Pandas' population recovered thanks to conservation efforts.",
            "Pandas can climb trees and swim well."
        ]
    },
    # add more animals here
    "giraffe": {
        "name": "Giraffe",
        "queries": ["giraffe eating leaves", "baby giraffe running", "giraffe herd"],
        "facts": [
            "Giraffes are the tallest land animals.",
            "A giraffe's neck can be up to 2 meters long.",
            "Giraffes have a long prehensile tongue about 45 cm.",
            "Their spots act like fingerprints — unique patterns.",
            "They only need to drink once every few days.",
            "Giraffes live in groups called towers.",
            "They sleep very little, often standing up.",
            "Calves can stand and run within hours of birth.",
            "Males fight by swinging their necks in 'necking' battles.",
            "Giraffe hearts are huge and pump hard to move blood uphill."
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
recent = state.get("recent_animals", [])

# choose animal not used recently
choices = list(FACTS_DB.keys())
random.shuffle(choices)
animal_key = None
for c in choices:
    if c not in recent:
        animal_key = c
        break
if animal_key is None:
    animal_key = choices[0]

data = FACTS_DB[animal_key]
title = f"10 Amazing Facts About {data['name']}"
scenes = []
idx = 1
for fact in data["facts"][:10]:
    scenes.append({
        "idx": idx,
        "headline": f"Fact {idx}",
        "text": fact,
        "query": random.choice(data["queries"]),
        # target seconds per fact: estimate by words (approx 0.5s/word) -> used later to prepare clips
        "estimated_words": len(fact.split())
    })
    idx += 1

description = f"{title}\n\nShort facts about the {data['name']}. Videos source: Pexels (royalty-free)."
tags = [data['name'].split()[0].lower(), "animal facts", "wildlife", "fun facts"]

script = {
    "title": title,
    "description": description,
    "tags": tags,
    "animal_key": animal_key,
    "scenes": scenes
}
open(os.path.join(OUT, "script.json"), "w", encoding="utf-8").write(json.dumps(script, ensure_ascii=False, indent=2))
print("Wrote output/script.json for", data['name'])

# update state (prevent repeating immediately)
recent.insert(0, animal_key)
recent = recent[:20]
state["recent_animals"] = recent
save_state(state)
print("Updated state recent_animals:", recent)
