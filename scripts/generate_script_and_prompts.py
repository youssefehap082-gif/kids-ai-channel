# scripts/generate_script_and_prompts.py
import json, os, random, time
OUT="output"
os.makedirs(OUT, exist_ok=True)
ts = int(time.time()) % 100000
title = f"10 Weird Facts | Episode {ts}"

# A template of 10 facts (you can change these or add randomness later)
facts = [
  ("Octopus has three hearts","An octopus has three hearts and blue blood."),
  ("Immortal jellyfish","A jellyfish species can revert to its juvenile form, effectively making it biologically immortal."),
  ("Crows recognize faces","Crows remember human faces and can keep grudges for years."),
  ("Frogs can freeze","Some frogs freeze solid in winter and thaw in spring without harm."),
  ("Honey never spoils","Archaeologists found edible honey in 3000-year-old tombs."),
  ("Sharks older than trees","Sharks existed before trees did on Earth."),
  ("Pistol shrimp shock","A pistol shrimp snaps its claw to create a bubble that stuns prey."),
  ("Axolotls regrow limbs","Axolotls can regenerate lost limbs and parts of organs."),
  ("Elephants mourn","Elephants display mourning behaviors for deceased herd members."),
  ("Tardigrades survive space","Tardigrades can survive the vacuum of space.")
]

scenes = []
for i, (h,t) in enumerate(facts, start=1):
    # craft prompt for image generation (clear, cartoon/storybook)
    prompt = f"{h}, {t} -- cartoon storybook illustration, cute, bright colors, 1280x720, clear character"
    scenes.append({"idx": i, "headline": h, "text": t, "prompt": prompt})

script = {"title": title, "scenes": scenes}
with open(os.path.join(OUT,"script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

# produce prompts.json for image gen
prompts = [{"scene_index": s["idx"], "prompt": s["prompt"]} for s in scenes]
with open(os.path.join(OUT,"prompts.json"), "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print("Wrote output/script.json and output/prompts.json")
