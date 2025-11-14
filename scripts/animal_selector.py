import random
from pathlib import Path
from .utils import read_json, write_json
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'data' / 'animal_database.json'
USED = ROOT / 'data' / 'used_animals.json'
def load_animals():
    arr = read_json(DB) or []
    return arr
def get_used():
    return read_json(USED) or []
def mark_used(name):
    used = get_used() or []
    if name in used: return
    used.insert(0, name)
    write_json(USED, used[:2000])
def pick_n_unique(n=2):
    animals = load_animals()
    if not animals: raise RuntimeError('DB empty')
    used = set(get_used() or [])
    candidates = [a for a in animals if a.get('name') not in used]
    if len(candidates) < n: candidates = animals
    picked = random.sample(candidates, k=min(n, len(candidates)))
    for p in picked: mark_used(p.get('name'))
    return picked
