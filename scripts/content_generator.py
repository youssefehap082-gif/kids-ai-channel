#!/usr/bin/env python3
import json, os

DB_PATH = 'data/animal_database.json'

def load_db():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_entry(name):
    db = load_db()
    name_lower = name.lower()
    for e in db:
        if e.get('name','').lower() == name_lower:
            return e
    return None

def generate_scientific(entry, n=10):
    facts = entry.get('facts', [])[:n]
    title = f"{entry['name'].title()} — 10 Scientific Facts"
    desc = entry.get('summary','') + "\n\n" + "\n".join(["- " + f for f in facts])
    return title, desc, facts

def generate_mixed(entry, n=10):
    facts = entry.get('facts', [])[:n]
    mixed = []
    for i, f in enumerate(facts):
        if i % 3 == 2:
            mixed.append(f + " Surprisingly, many people don't know this.")
        else:
            mixed.append(f)
    title = f"{entry['name'].title()} — 10 Surprising Facts"
    desc = entry.get('summary','') + "\n\n" + "\n".join(["- " + f for f in mixed])
    return title, desc, mixed

def generate_viral(entry, n=1):
    facts = entry.get('facts', [])
    headline = facts[0] if facts else f"{entry['name'].title()} is incredible."
    title = f"Did you know? {entry['name'].title()}"
    desc = headline + "\n#shorts"
    return title, desc, [headline]

def generate_for(name):
    entry = find_entry(name)
    if not entry:
        entry = {'name': name, 'summary': '', 'facts': [f"{name} is an animal."]}
    return {
        'scientific': generate_scientific(entry, 10),
        'mixed': generate_mixed(entry, 10),
        'viral': generate_viral(entry, 1)
    }

if __name__ == '__main__':
    import sys
    n = sys.argv[1] if len(sys.argv) > 1 else 'lion'
    print(generate_for(n))
