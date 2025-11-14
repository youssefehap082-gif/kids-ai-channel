# animal_selector.py - choose animals not used recently
import random
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'

def load_animals():
    return json.load(open(DATA / 'animal_database.json'))

def get_used():
    return json.load(open(DATA / 'used_animals.json'))

def mark_used(name):
    used = get_used()
    used.insert(0, name)
    used = used[:500]
    json.dump(used, open(DATA / 'used_animals.json'), indent=2)

def pick_n_unique(n=2):
    animals = load_animals()
    used = set(get_used())
    candidates = [a for a in animals if a['name'] not in used]
    if len(candidates) < n:
        candidates = animals
    picked = random.sample(candidates, k=n)
    for p in picked:
        mark_used(p['name'])
    return picked
    def get_used():
    data = json.load(open(DATA / 'used_animals.json'))
    if not isinstance(data, list):
        data = []
        json.dump(data, open(DATA / 'used_animals.json', 'w'), indent=2)
    return data

