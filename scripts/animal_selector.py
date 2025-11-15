# scripts/animal_selector.py
"""
Select animals for daily videos.

System:
- Reads basic animal list from data/animal_list.txt
- Generates animal_database.json on first run (from Wikipedia)
- Tracks used animals in used_animals.json to avoid repetition for 7 days
- Ensures random + no-repeat selection
"""

import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ANIMAL_LIST = DATA / "animal_list.txt"
ANIMAL_DB = DATA / "animal_database.json"
USED = DATA / "used_animals.json"


def load_list():
    """Load the raw names from the text list"""
    if not ANIMAL_LIST.exists():
        raise RuntimeError("animal_list.txt missing!")
    with open(ANIMAL_LIST, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines() if x.strip()]


def load_db():
    """Load database (with facts fetched by wikipedia)"""
    if not ANIMAL_DB.exists():
        return {}
    try:
        with open(ANIMAL_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def load_used():
    if not USED.exists():
        return []
    try:
        return json.load(open(USED, "r", encoding="utf-8"))
    except:
        return []


def save_used(lst):
    with open(USED, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2)


def pick_animals(n=7):
    """
    Picks N animals, avoids repeating animals used in last 7 days.
    """
    names = load_list()
    db = load_db()
    used = load_used()

    # Filter missing db entries
    names = [x for x in names if x in db]

    # Remove recently used
    candidates = [x for x in names if x not in used[:7]]
    if len(candidates) < n:
        # if fewer candidates, reset used
        used = []
        candidates = names

    random.shuffle(candidates)
    selected = candidates[:n]

    # Update used list (prepend)
    used = selected + used
    save_used(used[:100])  # keep memory small

    # Return data objects with facts + species
    return [db[x] for x in selected]
