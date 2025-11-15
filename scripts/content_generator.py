import random
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "data" / "animal_database.json"

def load_db():
    if not DB.exists():
        raise RuntimeError("animal_database.json is missing. Run fetch_wikipedia first.")
    with open(DB, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_facts_script(animal_name, num_facts_long=10, num_facts_short=1):
    """
    Generates:
      - long video script (10 facts)
      - short script (1 fact)
    """
    db = load_db()

    entry = next((x for x in db if x["name"].lower() == animal_name.lower()), None)
    if not entry:
        raise RuntimeError(f"No facts found in DB for {animal_name}")

    facts = entry["facts"]
    if len(facts) < num_facts_long:
        num_facts_long = len(facts)

    long_script = facts[:num_facts_long]
    short_script = [random.choice(facts)]

    return long_script, short_script
