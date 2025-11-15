#!/usr/bin/env python3
import argparse, os, sys, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--publish-mode', choices=['scheduled','production','test'], default='production')
args = parser.parse_args()

print(f"Starting MAIN runner in mode: {args.publish_mode}")

# Minimal high-level flow (replace these calls with your project's functions)
# 1) load animal list/database
ANIMAL_DB = Path('data/animal_database.json')
if not ANIMAL_DB.exists():
    print("No animal_database.json found — exiting. Run fetch_wikipedia or provide the DB.")
    sys.exit(1)

# 2) pick first animal for first-run publish (example)
db = json.loads(ANIMAL_DB.read_text(encoding='utf-8'))
first = db[0] if isinstance(db, list) and len(db) else None
if not first:
    print("Animal DB empty")
    sys.exit(1)

name = first if isinstance(first, str) else first.get('name', 'unknown')
print("Production first run: creating 1 long + 1 short for", name)

# The real implementation should call:
# - generate_facts_script(name) -> produces narration text
# - generate_voice_with_failover(text, preferred_gender='male')
# - fetch video clips from assets or Pexels/Pixabay
# - assemble_long_video and assemble_short
# - upload to YouTube via youtube uploader script (requires YT keys)
#
# Here we only show expected checks so the workflow fails with useful messages if missing:
assets_dir = Path('assets/clips') / name.replace(' ','_')
if not assets_dir.exists() or not any(assets_dir.iterdir()):
    raise RuntimeError(f"No local clips found for {name}. Add assets or enable Pexels/Pixabay keys.")

# If you have the full implementation, call it here.
print("All checks passed — call the pipeline functions now.")
# e.g. pipeline.process_one(name, publish_mode=args.publish_mode)
