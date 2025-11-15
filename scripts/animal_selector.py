import json
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_FILE = BASE / "data" / "animal_database.json"

def load_animals():
    if not DATA_FILE.exists():
        raise RuntimeError(f"Animal DB file not found: {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_n_unique(n=5):
    animals = load_animals()
    if len(animals) < n:
        raise RuntimeError("Not enough animals in DB")
    return random.sample(animals, n)
