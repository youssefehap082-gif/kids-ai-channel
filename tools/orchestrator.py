# tools/orchestrator.py
import os
import json
import random
import time
import traceback
from pathlib import Path

# imports from your project
try:
    from generator import generate_long_video, generate_short_video
    from optimizer import AIOptimizer
except Exception as e:
    # If imports fail, print helpful message and re-raise so Actions log shows the problem.
    print("[orchestrator] Failed to import project modules:", e)
    raise

ROOT = Path(".")
WORKDIR = Path("workspace")
ASSETS = WORKDIR / "assets"
LOGS = WORKDIR / "logs"
ANIMALS_FILE = Path("animals_list.txt")

# ensure folders exist
WORKDIR.mkdir(exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

# TEST_RUN env var: treat 'true','1','yes' as True
TEST_RUN = os.getenv("TEST_RUN", "true").lower() in ("1", "true", "yes")

def read_animals():
    if not ANIMALS_FILE.exists():
        print(f"[orchestrator] WARNING: {ANIMALS_FILE} not found. Using fallback list.")
        return ["lion", "elephant", "tiger", "giraffe", "dolphin"]
    try:
        lines = [l.strip() for l in ANIMALS_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines:
            raise ValueError("animals_list.txt empty")
        return lines
    except Exception as e:
        print("[orchestrator] Error reading animals_list.txt:", e)
        return ["lion", "elephant", "tiger", "giraffe", "dolphin"]

def pick_random_animal():
    animals = read_animals()
    return random.choice(animals)

def safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[orchestrator] ERROR running {func._name_}: {e}")
        traceback.print_exc()
        return {"error": str(e)}

def run_test_mode():
    print("🧪 TEST MODE: Creating 1 Long + 1 Shorts to confirm system works.")
    animal_long = pick_random_animal()
    animal_short = pick_random_animal()
    print(f"[orchestrator] Selected for long: {animal_long}, for short: {animal_short}")
    long_result = safe_call(generate_long_video, animal_long, True)
    short_result = safe_call(generate_short_video, animal_short)
    print("✅ Test Long Result:", json.dumps(long_result, default=str))
    print("✅ Test Shorts Result:", json.dumps(short_result, default=str))
    print("🎉 Test completed. Check YouTube and workspace/ for files.")
    return

def run_daily_mode():
    print("🚀 Starting full automation schedule.")
    # 2 long videos
    for i in range(2):
        animal = pick_random_animal()
        print(f"[orchestrator] Generating long video {i+1}/2 for {animal}")
        safe_call(generate_long_video, animal, False)
        time.sleep(2)  # small pause between tasks
    # 5 shorts
    for i in range(5):
        animal = pick_random_animal()
        print(f"[orchestrator] Generating short {i+1}/5 for {animal}")
        safe_call(generate_short_video, animal)
        time.sleep(1)
    # run optimizer
    try:
        opt = AIOptimizer()
        opt.run()
        print("[orchestrator] Optimizer run complete.")
    except Exception as e:
        print("[orchestrator] Optimizer failed:", e)
        traceback.print_exc()
    print("✅ Daily automation finished.")

def main():
    print(f"[orchestrator] START (TEST_RUN={TEST_RUN})")
    if TEST_RUN:
        run_test_mode()
    else:
        run_daily_mode()

if _name_ == "_main_":
    main()
