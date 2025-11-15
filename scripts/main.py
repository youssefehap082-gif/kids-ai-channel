#!/usr/bin/env python3
import argparse, os, json, random, time
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parent
DATA = ROOT / 'data'
TMP = ROOT / 'tmp'
DATA.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

from content_generator import generate_facts_script
from voice_generator import generate_voice_with_failover
from video_creator import assemble_long_video, assemble_short
from youtube_uploader import upload_video

parser = argparse.ArgumentParser()
parser.add_argument('--mode', default='production', choices=['production','test'])
args = parser.parse_args()

FIRST_FLAG = DATA / 'first_run_done'

def first_run_done():
    return FIRST_FLAG.exists()

def mark_first_run():
    FIRST_FLAG.write_text('done')

def load_animal_db():
    dbf = DATA / 'animal_database.json'
    if not dbf.exists():
        # fallback small set
        return [{'name': 'lion'},{'name':'elephant'}]
    return json.loads(dbf.read_text(encoding='utf-8'))

def fetch_visual_clips(animal_name):
    # Minimal stub: expects assets/music/ and assets/videos/ to be present,
    # or uses web APIs (Pexels/Pixabay) if keys set. Here we try local assets first.
    vids = []
    local_dir = ROOT / 'assets' / 'videos'
    if local_dir.exists():
        for p in local_dir.glob(f"*{animal_name}*"):
            vids.append(str(p))
    # if no local, the system will rely on Pexels/Pixabay callers in other code paths
    return vids

def process_one(animal, voice_gender='male'):
    name = animal.get('name')
    meta = generate_facts_script(name)
    clips = fetch_visual_clips(name)
    if not clips:
        # raise to show problem - in production you'd fetch online clips
        raise RuntimeError(f"No local clips found for {name}. Add assets or enable Pexels/Pixabay keys.")
    script_text = meta['script'] + "\n\nDon't forget to subscribe to WildFacts Hub for more!"
    voice = generate_voice_with_failover(script_text, preferred_gender=voice_gender)
    long_out = assemble_long_video(clips, voice, music_path=None, title_text=meta['title'])
    upload_video(str(long_out), meta['title'], meta['description'], tags=meta['tags'])
    # short: use first clip
    short_out = assemble_short(clips[0], music_path=None)
    upload_video(str(short_out), f"{name.title()} — Short", f"Short clip of {name} #shorts", tags=[name, "shorts"])
    return True

def run_production():
    db = load_animal_db()
    # first-run: do 1 long + 1 short (sanity)
    if not first_run_done():
        first = db[0]
        print("Production first run: creating 1 long + 1 short for", first['name'])
        try:
            process_one(first, voice_gender='male')
            mark_first_run()
        except Exception as e:
            print("First run failed:", e)
            raise
    else:
        # daily: 2 long + 6 shorts using next animals
        selected = db[:8] if len(db) >= 8 else db * 8
        genders = ['male','female'] * 4
        idx = 0
        # 2 longs
        for i in range(2):
            process_one(selected[idx], voice_gender=genders[idx%2])
            idx += 1
        # 6 shorts
        for j in range(6):
            process_one(selected[idx], voice_gender=genders[idx%2])
            idx += 1

if __name__ == "__main__":
    if args.mode == 'production':
        run_production()
    else:
        print("Test mode: not implemented for production run.")
