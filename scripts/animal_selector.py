#!/usr/bin/env python3
import json, random
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'data' / 'animal_database.json'
USED = ROOT / 'data' / 'used_animals.json'

def load_db():
    return json.load(open(DB, 'r', encoding='utf-8'))

def get_used():
    try:
        return json.load(open(USED, 'r', encoding='utf-8'))
    except Exception:
        return []

def mark_used(name):
    used = get_used()
    used.insert(0, name)
    used = used[:500]
    json.dump(used, open(USED, 'w', encoding='utf-8'), indent=2)

def pick_n(n=2):
    db = load_db()
    used = set(get_used())
    candidates = [e for e in db if e['name'] not in used]
    if len(candidates) < n:
        candidates = db
    picked = random.sample(candidates, k=n)
    for p in picked:
        mark_used(p['name'])
    return picked

if __name__ == '__main__':
    print([p['name'] for p in pick_n(3)])
