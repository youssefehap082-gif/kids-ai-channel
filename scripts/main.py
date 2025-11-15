#!/usr/bin/env python3
import os, json, random, logging
logging.basicConfig(level=logging.INFO)
TEST = os.getenv('TEST_RUN', 'true').lower() == 'true'

# local imports
from scripts.fetch_wikipedia import main as fetch_db
from scripts.content_generator import generate_for
from scripts.pexels_pixabay_fetcher import fetch_clips_best
from scripts.voice_generator import generate_voice
from scripts.video_creator import assemble_long, assemble_short
from scripts.youtube_uploader import upload
from scripts.animal_selector import pick_n

# ensure DB
if not os.path.exists('data/animal_database.json') or os.path.getsize('data/animal_database.json') < 10:
    logging.info("animal_database.json missing or small — generating from list")
    # call fetch_wikipedia script
    import subprocess
    subprocess.run(['python3', 'scripts/fetch_wikipedia.py', '--input', 'data/animal_list.txt', '--output', 'data/animal_database.json'], check=True)

db = json.load(open('data/animal_database.json', 'r', encoding='utf-8'))

def process_long(animal):
    name = animal['name']
    logging.info("Processing long for %s", name)
    meta = generate_for(name)['mixed']  # use mixed format for retention
    clips = fetch_clips_best(name)
    if not clips:
        raise RuntimeError("No clips found for " + name)
    script_text = "\n".join(meta[2]) + "\nDon't forget to subscribe and hit the bell for more!"
    voice_file = generate_voice(script_text)
    out = assemble_long(clips, voice_file, music=None, title_text=meta[0])
    res = upload(out, meta[0], meta[1], tags=[name, 'wildlife', 'animals'])
    logging.info("Uploaded long: %s", res.get('id', res))
    return res

def process_short(animal):
    name = animal['name']
    logging.info("Processing short for %s", name)
    meta = generate_for(name)['viral']
    clips = fetch_clips_best(name)
    if not clips:
        raise RuntimeError("No clips found for " + name)
    out = assemble_short(clips[0], music=None)
    res = upload(out, meta[0], meta[1], tags=[name, 'shorts'])
    logging.info("Uploaded short: %s", res.get('id', res))
    return res

if __name__ == '__main__':
    try:
        if TEST:
            logging.info("TEST MODE: Uploading 1 long + 1 short (first-run publishes immediately)")
            animals = random.sample(db, 2)
            try:
                process_long(animals[0])
            except Exception as e:
                logging.error("Long failed: %s", e)
            try:
                process_short(animals[1])
            except Exception as e:
                logging.error("Short failed: %s", e)
        else:
            logging.info("PRODUCTION MODE: create 2 longs + 4-6 shorts distributed")
            animals = random.sample(db, min(len(db), 8))
            for i in range(2):
                try:
                    process_long(animals[i])
                except Exception as e:
                    logging.error("Long failed: %s", e)
            shorts_count = random.choice([4,5,6])
            for i in range(shorts_count):
                try:
                    process_short(animals[2 + i])
                except Exception as e:
                    logging.error("Short failed: %s", e)
    except Exception as ex:
        logging.exception("Fatal error in main: %s", ex)
        raise
