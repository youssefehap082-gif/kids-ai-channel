# scripts/main.py
#!/usr/bin/env python3
"""
Main orchestrator for YouTube animal automation.

Behavior:
- If TEST_RUN env var is true -> publish 1 long + 1 short immediately (test-first-run behavior).
- If TEST_RUN is false -> production: create 2 longs + 4-6 shorts per run, schedule publish times for the day.
- Ensures DB exists (calls scripts/fetch_wikipedia.py to populate data/animal_database.json).
- Uses pexels_pixabay_fetcher.fetch_clips_best for clips.
- Uses voice_generator.generate_voice_with_failover(text, preferred_gender) for TTS fallback.
- Uses video_creator.assemble_long_video / assemble_short for rendering.
- Uses youtube_uploader.upload(file, title, desc, tags, publishAt) for uploading and verification.
- Records successes/failures to data/performance_data.json.
"""

import os
import sys
import json
import random
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'scripts'
DATA = ROOT / 'data'
TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('main_orchestrator')

# Environment flags
TEST = os.getenv('TEST_RUN', 'true').lower() == 'true'

# Local imports (assumes files exist)
try:
    from scripts.animal_selector import pick_n
    from scripts.content_generator import generate_for
    from scripts.pexels_pixabay_fetcher import fetch_clips_best
    from scripts.voice_generator import generate_voice_with_failover
    from scripts.video_creator import assemble_long_video, assemble_short
    from scripts.youtube_uploader import upload as yt_upload, get_youtube_service
    from scripts.utils import download_file
except Exception as e:
    log.exception("Local import failed. Ensure scripts are in scripts/*.py and PYTHONPATH set. Error: %s", e)
    raise

ANIMAL_DB = DATA / 'animal_database.json'
USED_FILE = DATA / 'used_animals.json'
PERF_FILE = DATA / 'performance_data.json'


def ensure_files():
    if not USED_FILE.exists():
        USED_FILE.write_text("[]", encoding='utf-8')
    if not PERF_FILE.exists():
        PERF_FILE.write_text("{}", encoding='utf-8')


def ensure_db_from_list():
    """
    If animal_database.json missing or very small, call the fetch_wikipedia script to build it from animal_list.txt
    """
    if not ANIMAL_DB.exists() or ANIMAL_DB.stat().st_size < 10:
        log.info("animal_database.json missing or small — generating from list")
        # call fetch_wikipedia script
        import subprocess
        input_list = ROOT / 'data' / 'animal_list.txt'
        if not input_list.exists():
            raise RuntimeError("data/animal_list.txt missing. Provide the seed list.")
        subprocess.run([sys.executable, str(SCRIPTS / 'fetch_wikipedia.py'), '--input', str(input_list), '--output', str(ANIMAL_DB)], check=True)
        log.info("Wrote %s", ANIMAL_DB)


def load_db():
    with open(ANIMAL_DB, 'r', encoding='utf-8') as f:
        return json.load(f)


def mark_performance(video_id, animal_name, kind, meta):
    """
    Save performance record (initial) - will be enriched by periodic analyzer.
    """
    try:
        perf = json.loads(PERF_FILE.read_text(encoding='utf-8'))
    except Exception:
        perf = {}
    perf.setdefault(animal_name, []).append({'id': video_id, 'kind': kind, 'meta': meta, 'time': datetime.utcnow().isoformat()})
    PERF_FILE.write_text(json.dumps(perf, indent=2), encoding='utf-8')


def verify_upload(video_id):
    """
    Use YouTube Data API to verify that the uploaded video is available.
    Returns True if found and accessible.
    """
    try:
        youtube = get_youtube_service()
        res = youtube.videos().list(part='status,snippet', id=video_id).execute()
        items = res.get('items', [])
        return len(items) == 1
    except Exception as e:
        log.warning("verify_upload failed: %s", e)
        return False


def publish_time_for_slot(slot_hour):
    """
    Given slot hour (UTC int or datetime), return ISO 8601 time in future (today or tomorrow) for scheduling.
    We'll schedule for today at that hour if still in future, otherwise tomorrow.
    """
    now = datetime.now(timezone.utc)
    if isinstance(slot_hour, int):
        candidate = datetime(now.year, now.month, now.day, slot_hour, 0, tzinfo=timezone.utc)
    elif isinstance(slot_hour, datetime):
        candidate = slot_hour.astimezone(timezone.utc)
    else:
        raise ValueError("slot_hour must be int or datetime")
    if candidate <= now:
        candidate = candidate + timedelta(days=1)
    return candidate.isoformat(timespec='seconds') + 'Z'  # ISO with Z


def process_long_for_animal(animal_entry, voice_gender='male', schedule_time_iso=None):
    """
    Create 1 long video for animal_entry and upload. If schedule_time_iso provided, pass as publishAt.
    Returns upload response or raise.
    """
    name = animal_entry['name']
    log.info("Starting long for %s", name)
    # Generate meta (choose mixed for retention)
    meta = generate_for(name)['mixed']  # (title, desc, facts_list)
    title, description, facts = meta

    # fetch clips
    clips = []
    try:
        clips = fetch_clips_best(name)
    except Exception as e:
        log.warning("Clip fetch error (long) for %s: %s", name, e)
    if not clips:
        raise RuntimeError(f"No clips found for long: {name}")

    # prepare script (join facts into narration) + CTA
    script_text = "\n".join(facts[:10]) + "\n\nDon't forget to subscribe and hit the bell for more!"

    # generate voice (failover)
    try:
        voice_file = generate_voice_with_failover(script_text, preferred_gender=voice_gender)
    except Exception as e:
        log.exception("TTS failed for %s: %s", name, e)
        raise RuntimeError(f"TTS failed for long {name}: {e}")

    # pick music: optional - expects assets/music or pick nothing (can be extended)
    music_path = None
    local_music_folder = ROOT / 'assets' / 'music'
    if local_music_folder.exists():
        mp3s = list(local_music_folder.glob('*.mp3'))
        if mp3s:
            music_path = str(random.choice(mp3s))

    # assemble
    try:
        out = assemble_long_video(clips, str(voice_file), music_path, title_text=title)
    except Exception as e:
        log.exception("Video assemble failed (long) for %s: %s", name, e)
        raise

    # prepare tags
    tags = [name, 'wildlife', 'animals', 'facts']

    # prepare publish options (YouTube API: status.publishAt)
    publishAt = None
    if schedule_time_iso:
        publishAt = schedule_time_iso

    # upload (youtube_uploader.upload should accept publishAt param if implemented; fallback to immediate)
    try:
        log.info("Uploading long: %s", out)
        # if yt_upload supports publishAt via kwarg
        try:
            res = yt_upload(out, title, description, tags=tags, publishAt=publishAt)
        except TypeError:
            # uploader doesn't accept publishAt param -> upload immediate
            res = yt_upload(out, title, description, tags=tags)
    except Exception as e:
        log.exception("YouTube upload failed for long %s: %s", name, e)
        raise

    # verify upload
    vid_id = None
    try:
        vid_id = res.get('id') if isinstance(res, dict) else getattr(res, 'get', lambda k: None)('id')
    except Exception:
        # try to parse
        try:
            vid_id = res['id']
        except Exception:
            vid_id = None

    if not vid_id:
        log.warning("Upload returned no id; attempting to parse response: %s", res)
    else:
        ok = verify_upload(vid_id)
        if not ok:
            log.warning("verify_upload returned False for id %s. The upload object: %s", vid_id, res)
        else:
            log.info("Verified upload for long %s -> id=%s", name, vid_id)
            mark_performance(vid_id, name, 'long', {'title': title, 'publishAt': publishAt})

    return res


def process_short_for_animal(animal_entry, schedule_time_iso=None):
    """
    Create 1 short (music only) and upload. schedule_time_iso optional (but Shorts usually immediate).
    """
    name = animal_entry['name']
    log.info("Starting short for %s", name)
    meta = generate_for(name)['viral']
    title, description, facts = meta

    # fetch one clip
    clips = []
    try:
        clips = fetch_clips_best(name)
    except Exception as e:
        log.warning("Clip fetch error (short) for %s: %s", name, e)
    if not clips:
        raise RuntimeError(f"No clips found for short: {name}")

    clip = clips[0]
    # pick music
    music_path = None
    local_music_folder = ROOT / 'assets' / 'music'
    if local_music_folder.exists():
        mp3s = list(local_music_folder.glob('*.mp3'))
        if mp3s:
            music_path = str(random.choice(mp3s))

    try:
        out_short = assemble_short(clip, music_path)
    except Exception as e:
        log.exception("Failed assembling short for %s: %s", name, e)
        raise

    tags = [name, 'shorts', 'animals']
    try:
        log.info("Uploading short: %s", out_short)
        try:
            res = yt_upload(out_short, title, description, tags=tags, publishAt=schedule_time_iso)
        except TypeError:
            res = yt_upload(out_short, title, description, tags=tags)
    except Exception as e:
        log.exception("YouTube upload failed for short %s: %s", name, e)
        raise

    vid_id = None
    try:
        vid_id = res.get('id') if isinstance(res, dict) else getattr(res, 'get', lambda k: None)('id')
    except Exception:
        try:
            vid_id = res['id']
        except Exception:
            vid_id = None

    if vid_id:
        ok = verify_upload(vid_id)
        if ok:
            log.info("Verified upload short %s -> id=%s", name, vid_id)
            mark_performance(vid_id, name, 'short', {'title': title, 'publishAt': schedule_time_iso})
        else:
            log.warning("Short upload not verified id=%s", vid_id)
    else:
        log.warning("Short upload returned no id: %s", res)

    return res


def run_test_first_run(db):
    """
    TEST mode behavior: upload 1 long + 1 short immediately, using first two random animals.
    """
    log.info("TEST MODE: Uploading 1 long + 1 short (first-run publishes immediately)")
    animals = random.sample(db, min(len(db), 2))
    failures = []
    try:
        process_long_for_animal(animals[0], voice_gender='male')
    except Exception as e:
        log.exception("Long failed (test): %s", e)
        failures.append(('long', animals[0]['name'], str(e)))
    try:
        process_short_for_animal(animals[1])
    except Exception as e:
        log.exception("Short failed (test): %s", e)
        failures.append(('short', animals[1]['name'], str(e)))
    if failures:
        log.error("Test run had failures: %s", failures)
    else:
        log.info("Test run successful")


def run_production(db):
    """
    Production behavior:
    - pick 2 animals for long videos, schedule them for appropriate publish times
    - pick 4-6 animals for shorts and schedule or publish accordingly
    """
    log.info("PRODUCTION MODE: create 2 longs + 4-6 shorts distributed")
    # choose 8 distinct animals (or less if DB small)
    total_needed = 2 + 6
    pool = random.sample(db, min(len(db), total_needed))
    # schedule publish times (UTC) for longs and shorts
    # Predefined optimal slots (UTC) — these can be tuned
    long_slots = [7, 18]  # 07:00, 18:00
    short_slots = [8, 11, 14, 17, 20, 23]  # 6 shorts possible
    # Cap short_count to available animals
    short_count = min(6, max(4, len(pool) - 2))
    # Map animals
    long_animals = pool[:2]
    short_animals = pool[2:2+short_count]

    # Process longs with scheduling
    for i, animal in enumerate(long_animals):
        try:
            publish_iso = publish_time_for_slot(long_slots[i % len(long_slots)])
            process_long_for_animal(animal, voice_gender='male' if i % 2 == 0 else 'female', schedule_time_iso=publish_iso)
        except Exception as e:
            log.exception("Long failed (prod) for %s: %s", animal['name'], e)
            # continue to next

    # Process shorts
    for i, animal in enumerate(short_animals):
        try:
            # use slot by index
            publish_iso = publish_time_for_slot(short_slots[i % len(short_slots)])
            process_short_for_animal(animal, schedule_time_iso=publish_iso)
        except Exception as e:
            log.exception("Short failed (prod) for %s: %s", animal['name'], e)


def main():
    ensure_files()
    ensure_db_from_list()
    db = load_db()
    if not db:
        raise RuntimeError("animal database empty")

    if TEST:
        run_test_first_run(db)
    else:
        run_production(db)
    log.info("Main finished")


if __name__ == '__main__':
    try:
        log.info("Starting main orchestrator. TEST=%s", TEST)
        main()
    except Exception as exc:
        log.exception("Fatal error in main: %s", exc)
        sys.exit(1)
