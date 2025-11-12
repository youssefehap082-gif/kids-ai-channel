# tools/orchestrator.py
import os
import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from generator import generate_long_video, generate_short_video
from optimizer import AIOptimizer

WORKDIR = Path("workspace")
ASSETS = Path("workspace/assets")
LOGS = Path("workspace/logs")
ANIMALS_FILE = Path("animals_list.txt")

os.makedirs(WORKDIR, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

TEST_RUN = os.getenv("TEST_RUN","false").lower() in ("1","true","yes")

def pick_animals(n, used=set()):
    animals = [a.strip() for a in ANIMALS_FILE.read_text(encoding='utf-8').splitlines() if a.strip()]
    # rotate to avoid repeats: simple approach: shuffle and pick first n not in used
    random.shuffle(animals)
    picked = []
    for a in animals:
        if a in used:
            continue
        picked.append(a)
        if len(picked) >= n:
            break
    # fallback if not enough unused
    if len(picked) < n:
        for a in animals:
            if a not in picked:
                picked.append(a)
            if len(picked) >= n:
                break
    return picked

def load_used_log():
    p = WORKDIR / "used_animals.json"
    if not p.exists():
        return {"used": []}
    return json.loads(p.read_text(encoding='utf-8'))

def save_used_log(d):
    p = WORKDIR / "used_animals.json"
    p.write_text(json.dumps(d, indent=2), encoding='utf-8')

def main():
    # load used animals (past 7 days)
    used = load_used_log()
    recent_used = set(used.get("used",[]))
    if TEST_RUN:
        print("TEST_RUN mode: will create and upload ONE long video only (test).")
        animals = pick_animals(1, used=recent_used)
        result = generate_long_video(animals[0], test_run=True)
        print("Test run created:", result)
        return

    # Normal daily run:
    # 2 long videos (different animals)
    long_animals = pick_animals(2, used=recent_used)
    for idx, animal in enumerate(long_animals):
        print(f"Generating long video {idx+1}/2 for {animal}")
        generate_long_video(animal, test_run=False)

    # 5 shorts
    short_animals = pick_animals(5, used=recent_used.union(set(long_animals)))
    for idx, animal in enumerate(short_animals):
        print(f"Generating short {idx+1}/5 for {animal}")
        generate_short_video(animal)

    # update used log (append new used and keep last 21 entries)
    new_used = list(recent_used.union(set(long_animals)).union(set(short_animals)))
    # rotate: keep last 42 entries for safety
    used["used"] = (used.get("used",[]) + long_animals + short_animals)[-42:]
    save_used_log(used)

    # run optimizer (analyze last 30 days and produce style profile)
    optimizer = AIOptimizer()
    optimizer.run()  # will fetch analytics and save recommendations

if _name_ == "_main_":
    main()

