# scripts/generate_script_animal.py
import json, os, time, random
OUT = "output"
os.makedirs(OUT, exist_ok=True)

# If you want a specific animal, set environment variable ANIMAL (e.g., ANIMAL=panda)
animal_env = os.environ.get("ANIMAL", "").strip().lower()

# Small facts database for common animals (extendable)
FACTS_DB = {
    "panda": {
        "name": "Giant Panda",
        "queries": ["panda eating bamboo", "panda cub playing", "giant panda forest"],
        "brief": "Pandas live mainly in bamboo forests in China. They spend much of the day eating bamboo.",
        "facts": [
            "Their diet is over 99% bamboo.",
            "An adult panda can eat up to 38 kg of bamboo a day.",
            "Baby pandas are born very small—about the size of a cup of tea.",
            "Pandas have a pseudo-thumb to help them hold bamboo."
        ]
    },
    "lion": {
        "name": "Lion",
        "queries": ["lion in savanna", "lion cub playing", "lion pride"],
        "brief": "Lions are social big cats that live in groups called prides, mostly in Africa.",
        "facts": [
            "A pride is usually made of related females, their cubs, and a small number of males.",
            "Male lions have manes which can indicate health and strength.",
            "Lions are skilled cooperative hunters, mostly active at night."
        ]
    },
    "dolphin": {
        "name": "Dolphin",
        "queries": ["dolphin swimming", "dolphin jumping", "baby dolphin"],
        "brief": "Dolphins are highly intelligent marine mammals known for playful behavior.",
        "facts": [
            "Dolphins use echolocation to find food and navigate.",
            "They have complex social structures and can use teamwork to hunt.",
            "Some species are known to show altruistic behavior."
        ]
    },
    "owl": {
        "name": "Owl",
        "queries": ["owl flying", "owl close up", "baby owl"],
        "brief": "Owls are nocturnal birds known for silent flight and large eyes.",
        "facts": [
            "Owls can rotate their heads nearly 270 degrees.",
            "They have special feathers that allow silent flight.",
            "Many owls hunt at night using excellent hearing."
        ]
    },
    "elephant": {
        "name": "Elephant",
        "queries": ["elephant herd", "baby elephant", "elephant drinking water"],
        "brief": "Elephants are large land mammals with strong social bonds and long memories.",
        "facts": [
            "Elephants use their trunks for breathing, smelling, touching and grabbing.",
            "They have complex social structures and rituals around the dead.",
            "Elephants can communicate with low-frequency sounds over long distances."
        ]
    }
}

# fallback animal list
fallback_animals = list(FACTS_DB.keys())

if animal_env and animal_env in FACTS_DB:
    animal_key = animal_env
else:
    animal_key = random.choice(fallback_animals)

data = FACTS_DB[animal_key]
title = f"All About {data['name']} — 7 Amazing Facts"
# create narration: intro + facts sections + outro
intro = f"Meet the {data['name']}! {data['brief']}"
facts_texts = data["facts"]
scenes = []
# we'll create one scene per fact + intro + outro
idx = 1
# intro scene
scenes.append({
    "idx": idx,
    "headline": "Introduction",
    "query": data["queries"][0],
    "caption": f"Introduction: {data['brief']}",
    "text": intro
})
idx += 1
# facts scenes
for f in facts_texts:
    scenes.append({
        "idx": idx,
        "headline": f"Fact {idx-1}",
        "query": random.choice(data["queries"]),
        "caption": f,
        "text": f"{f}"
    })
    idx += 1
# outro
outro_text = "Thanks for watching! Subscribe for daily animal facts and hit the bell to not miss the next video."
scenes.append({
    "idx": idx,
    "headline": "Wrap up",
    "query": data["queries"][-1],
    "caption": "Thanks for watching!",
    "text": outro_text
})

# SEO fields
description_lines = [
    title,
    "",
    "Today we learn quick facts about the " + data['name'] + ".",
    "",
    "Videos source: Pexels (royalty-free clips).",
    "",
    "Subscribe for daily animal facts!"
]
description = "\n".join(description_lines)
tags = [data['name'].split()[0].lower(), "animal facts", "wildlife", "fun facts", "nature"]
hashtags = ["#animals", "#facts", f"#{data['name'].split()[0]}"]

script = {
    "title": title,
    "description": description,
    "tags": tags,
    "hashtags": hashtags,
    "animal_key": animal_key,
    "scenes": scenes
}

with open(os.path.join(OUT,"script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

print("Wrote output/script.json — animal:", data['name'])
