# scripts/generate_story.py
import json, os, time, random
OUT = "output"
os.makedirs(OUT, exist_ok=True)

# You can add more templates/themes here to get varied stories
STORY_TEMPLATES = [
    {
        "title_base": "The Little Star Adventure",
        "beats": [
            ("Intro", "Max and Sam find a mysterious map that leads to a tiny star."),
            ("Plan", "They decide to follow the map and prepare a small backpack."),
            ("Journey", "On their way they meet friendly animals and solve puzzles."),
            ("Trouble", "A rainstorm tests their courage but they keep helping each other."),
            ("Discovery", "They reach a glowing tree and find the little star lost on a branch."),
            ("Return", "They safely return the star to the sky and celebrate with friends.")
        ]
    },
    {
        "title_base": "The Magic Garden",
        "beats": [
            ("Intro", "Luna finds a secret key in her garden."),
            ("Exploration", "The key opens a door to a garden that changes colors."),
            ("Friend", "She meets a talking bee who becomes her friend."),
            ("Challenge", "The garden wilts and they must find water from the singing well."),
            ("Restore", "Together they sing and the garden returns to life."),
            ("Celebration", "The town celebrates the new magical garden.")
        ]
    }
]

# pick a random template and create a multi-scene story (~6 scenes, aim >= 5 minutes)
tpl = random.choice(STORY_TEMPLATES)
ts = int(time.time()) % 100000
title = f"{tpl['title_base']} | Episode {ts}"

scenes = []
scene_durations = []  # estimated seconds per scene (we will aim for 60+ seconds per scene to reach 6+ min total)
for i, (heading, summary) in enumerate(tpl["beats"], start=1):
    # craft a child-friendly paragraph for narration (extend summary)
    paragraph = f"{summary} {heading} continues with fun details: {summary} They learn something important and laugh together."
    # whiteboard display text: split into 2-4 short lines
    words = paragraph.split()
    # split into approx 3 lines
    part = max(1, len(words) // 3)
    wb_lines = [" ".join(words[j:j+part]) for j in range(0, len(words), part)]
    wb_text = "\n".join(wb_lines[:4])  # keep up to 4 lines
    prompt = f"{heading}: {summary} -- cute child-friendly 2D illustration, storybook cartoon, center subject, bright, 1280x720"
    scenes.append({
        "idx": i,
        "headline": heading,
        "text": paragraph,
        "whiteboard_text": wb_text,
        "prompt": prompt
    })
    # estimate ~60-90s per scene (audio length depends on narration; we'll let gTTS determine)
    scene_durations.append(70)

script = {"title": title, "scenes": scenes}
with open(os.path.join(OUT, "script.json"), "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

# prompts for image generation
prompts = [{"scene_index": s["idx"], "prompt": s["prompt"]} for s in scenes]
with open(os.path.join(OUT, "prompts.json"), "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print("Wrote output/script.json and output/prompts.json")
print("Title:", title)
