# tools/orchestrator.py
import os
import json
import random
import time
from pathlib import Path
from generator import generate_long_video, generate_short_video
from optimizer import AIOptimizer

ROOT = Path(".")
WORKDIR = Path("workspace")
ASSETS = WORKDIR / "assets"
LOGS = WORKDIR / "logs"
ANIMALS_FILE = Path("animals_list.txt")

WORKDIR.mkdir(exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

TEST_RUN = os.getenv("TEST_RUN", "true").lower() in ("1","true","yes")

def read_animals():
    lines = [l.strip() for l in ANIMALS_FILE.read_text(encoding='utf-8').splitlines() if l.strip()]
    return lines

def pick_random_animal():
    animals = read_animals()
    return random.choice(animals)

def main():
    # If TEST_RUN => create one long video only (unlisted) to test
    if TEST_RUN:
        animal = pick_random_animal()
        print(f"[Orchestrator] TEST_RUN: generating single test long video for '{animal}'")
        res = generate_long_video(animal, test_run=True)
        print("[Orchestrator] Test result:", res)
        return

    # Normal daily run:
    # 2 long videos
    for i in range(2):
        animal = pick_random_animal()
        print(f"[Orchestrator] Generating long video {i+1}/2 for {animal}")
        generate_long_video(animal, test_run=False)

    # 5 shorts
    for i in range(5):
        animal = pick_random_animal()
        print(f"[Orchestrator] Generating short {i+1}/5 for {animal}")
        generate_short_video(animal)

    # run optimizer
    opt = AIOptimizer()
    opt.run()
    print("[Orchestrator] Daily run completed.")

if _name_ == "_main_":
    main()
