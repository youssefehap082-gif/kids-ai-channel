#!/usr/bin/env python3
# scripts/generate_script_facts.py
# Generate a simple script with 10 facts for an animal (fallback local DB).
import os, json, random
OUT = "output"
STATE_DIR = "state"
STATE_FILE = os.path.join(STATE_DIR, "state.json")
os.makedirs(OUT, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

FACTS_DB = {
    "panda": {
        "name": "Giant Panda",
        "queries": ["panda", "panda bamboo", "panda cub playing", "giant panda forest"],
        "facts": [
            "Pandas live mainly in bamboo forests in China.",
            "Pandas spend up to 14 hours a day eating bamboo.",
            "An adult panda can eat roughly 20 to 40 kilograms of bamboo daily.",
            "Baby pandas are born blind and tiny compared to their mothers.",
            "Pandas have a pseudo-thumb to help hold bamboo while eating.",
            "Pandas are generally solitary animals and mark territory with scent.",
            "Their black and white fur helps camouflage them in snow and forests.",
            "Pandas can climb trees and are surprisingly good swimmers.",
            "Conservation efforts helped panda numbers slowly recover.",
            "Pandas communicate using vocalizations and scent markings."
        ]
    },
    "giraffe": {
        "name": "Giraffe",
        "queries": ["giraffe", "giraffe eating leaves", "baby giraffe"],
        "facts": [
            "Giraffes are the tallest land animals.",
            "A giraffe's neck can reach up to 2 meters long.",
            "They have a 45-centimeter long prehensile tongue.",
            "Each giraffe's spot pattern is unique like fingerprints.",
            "They live in groups called towers.",
            "Giraffes have powerful hearts to pump blood up the neck.",
            "Calves can stand and run within hours of birth.",
            "Giraffes sleep very little and often do so standing up.",
            "They drink water infrequently and can go days without it.",
            "Males fight by swinging their necks in a behavior called necking."
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
    "description": f"{title}\nClips source: Pexels (royalty-free).",
    "tags": [data["name"].split()[0].lower(), "animal facts", "wildlife", "fun facts"],
    "animal_key": animal_key,
    "scenes": scenes
}

open(os.path.join(OUT, "script.json"), "w", encoding="utf-8").write(json.dumps(script, ensure_ascii=False, indent=2))
print("WROTE output/script.json for", data["name"])

# update state
recent.insert(0, animal_key)
recent = recent[:20]
state["recent"] = recent
save_state(state)
print("Updated state:", recent)
