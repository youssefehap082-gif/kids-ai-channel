# scripts/generate_script_animal.py
import json, os, time, random
OUT = "output"
STATE_DIR = "state"
STATE_FILE = os.path.join(STATE_DIR, "state.json")
os.makedirs(OUT, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

# small DB - extendable
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
    },
    "cat": {
        "name": "Cat",
        "queries": ["cute cat playing", "kitten sleeping", "cat close up"],
        "brief": "Cats are small carnivores domesticated thousands of years ago.",
        "facts": [
            "Cats sleep up to 16 hours a day.",
            "They have excellent night vision.",
            "Cats use whiskers to sense their surroundings."
        ]
    },
    "dog": {
        "name": "Dog",
        "queries": ["puppy playing", "dog running", "cute dog close up"],
        "brief": "Dogs are domesticated mammals known for loyalty and companionship.",
        "facts": [
            "Dogs have a sense of smell thousands of times better than humans.",
            "They can be trained to perform a wide range of tasks.",
            "Different breeds have very different behaviors and skills."
        ]
    }
}

# state functions
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE, encoding="utf-8"))
        except:
            return {}
    return {}

def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

state = load_state()
recent = state.get("recent_animals", [])  # list of recent animals (most recent first)

# pick an animal that is not in recent (lookback of len(recent) maybe 5)
choices = list(FACTS_DB.keys())
random.shuffle(choices)
animal_key = None
for c in choices:
    if c not in recent:
        animal_key = c
        break
if animal_key is None:
    # everything used recently; pick randomly but not same as last
    animal_key = random.choice(choices)
    if recent and animal_key == recent[0] and len(choices)>1:
        animal_key = choices[1]

data = FACTS_DB[animal_key]
title = f"All About {data['name']} — {len(data['facts'])} Amazing Facts"

# Build scenes: intro + facts + outro
scenes = []
idx = 1
scenes.append({
    "idx": idx,
    "headline": "Introduction",
    "query": data["queries"][0],
    "caption": f"Intro: {data['brief']}",
    "text": f"Meet the {data['name']}. {data['brief']}"
})
idx += 1
for f in data["facts"]:
    scenes.append({
        "idx": idx,
        "headline": f"Fact {idx-1}",
        "query": random.choice(data["queries"]),
        "caption": f,
        "text": f
    })
    idx += 1
scenes.append({
    "idx": idx,
    "headline": "Wrap up",
    "query": data["queries"][-1],
    "caption": "Thanks for watching! Subscribe for daily animal facts.",
    "text": "Thanks for watching! Subscribe for daily animal facts and hit the bell."
})

# SEO fields
description_lines = [
    title,
    "",
    f"Today we learn quick facts about the {data['name']}.",
    "",
    "Videos source: Pexels (royalty-free).",
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

open(os.path.join(OUT,"script.json"), "w", encoding="utf-8").write(json.dumps(script, ensure_ascii=False, indent=2))
print("Wrote output/script.json — animal:", data['name'])

# update state: push this animal to recent (keep last 5)
recent.insert(0, animal_key)
recent = recent[:5]
state["recent_animals"] = recent
save_state(state)
print("Updated state recent_animals:", recent)
