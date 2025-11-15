#!/usr/bin/env python3
import os, sys, argparse, random, json
from pathlib import Path
from scripts.animal_selector import pick_n_unique
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import generate_voice_with_failover
from scripts.video_creator import assemble_long_video, assemble_short, make_title_image
from scripts.youtube_uploader import upload_video_with_caption
from scripts.utils import ensure_tmp, fetch_clips_for_animal, read_json, write_json

BASE = Path(__file__).resolve().parent
TMP = BASE / "tmp"
TMP.mkdir(exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--publish-mode", choices=["production","test","scheduled"], default="production")
args = parser.parse_args()

# configuration
LONG_TARGET_SECONDS = 180  # 3 minutes
SHORT_VOICE_SECONDS = 15
SHORT_MAX_SECONDS = 60
VIDEO_RESOLUTION = "1080p"

def run_once_test():
    animals = pick_n_unique(2)
    print("Selected test animals:", [a['name'] for a in animals])
    # produce 1 long + 1 short
    long_an = animals[0]
    short_an = animals[1]
    try:
        clips_long = fetch_clips_for_animal(long_an)
        meta = generate_facts_script(long_an['name'])
        script_text = meta['script'] + "\\n\\nDon't forget to subscribe and hit the bell for more!"
        voice = generate_voice_with_failover(script_text, preferred_gender='male')
        music = None
        watermark = str(BASE.parent / 'assets' / 'watermark.png') if (BASE.parent / 'assets' / 'watermark.png').exists() else None
        long_file = assemble_long_video(clips_long, voice_path=voice, music_path=music, title_text=meta['title'], watermark_path=watermark)
        uploaded = upload_video_with_caption(long_file, meta['title'], meta['description'], tags=meta['tags'])
        print("Uploaded long:", uploaded.get('id') if uploaded else uploaded)
    except Exception as e:
        print("First long failed:", e)

    try:
        clips_short = fetch_clips_for_animal(short_an)
        # pick first clip for short
        if not clips_short:
            raise RuntimeError("No clips for short")
        voice_short = generate_voice_with_failover("One amazing fact about " + short_an['name'], preferred_gender='female')
        music = None
        short_file = assemble_short(clips_short[0], music_path=music, voice_path=voice_short, watermark_path=watermark)
        uploaded_s = upload_video_with_caption(short_file, f"{short_an['name'].title()} — Short", f"Short clip of {short_an['name']}", tags=[short_an['name'],'shorts'])
        print("Uploaded short:", uploaded_s.get('id') if uploaded_s else uploaded_s)
    except Exception as e:
        print("First short failed:", e)

def run_production_cycle():
    # produce 2 longs + 5-6 shorts (this job can be split across runs if needed)
    animals = pick_n_unique(7)
    sexes = ['male','female']
    uploaded_ids = []
    for i in range(2):
        an = animals[i]
        try:
            clips = fetch_clips_for_animal(an)
            meta = generate_facts_script(an['name'])
            voice = generate_voice_with_failover(meta['script'] + "\\n\\nDon't forget to subscribe and hit the bell for more!", preferred_gender=sexes[i%2])
            watermark = str(BASE.parent / 'assets' / 'watermark.png') if (BASE.parent / 'assets' / 'watermark.png').exists() else None
            out = assemble_long_video(clips, voice_path=voice, music_path=None, title_text=meta['title'], watermark_path=watermark)
            res = upload_video_with_caption(out, meta['title'], meta['description'], tags=meta['tags'])
            uploaded_ids.append(res.get('id') if res else None)
        except Exception as e:
            print("Long failed for", an['name'], e)
    # Shorts
    for j, an in enumerate(animals[2:2+5]):
        try:
            clips = fetch_clips_for_animal(an)
            if not clips:
                continue
            voice = generate_voice_with_failover("Quick fact: " + an['name'], preferred_gender='female')
            out = assemble_short(clips[0], music_path=None, voice_path=voice, watermark_path=watermark)
            res = upload_video_with_caption(out, f"{an['name'].title()} — Short", f"Short clip of {an['name']}", tags=[an['name'],'shorts'])
            uploaded_ids.append(res.get('id') if res else None)
        except Exception as e:
            print("Short failed for", an['name'], e)

    print("Uploaded IDs:", uploaded_ids)

if __name__ == "__main__":
    if args.publish_mode == "test":
        run_once_test()
    else:
        run_production_cycle()
