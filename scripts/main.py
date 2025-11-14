import os, random, time
from pathlib import Path
from scripts.animal_selector import pick_n_unique
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import generate_voice_with_failover
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.youtube_uploader import upload_video
ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / 'tmp'; TMP.mkdir(exist_ok=True)
TEST = False  # PRODUCTION: set False to upload directly
def fetch_clips_for_animal(animal):
    # very simple wrappers using Pexels/Pixabay
    return []
def pick_music():
    m = ROOT / 'assets' / 'music'
    return next(iter(m.glob('*.mp3')), None)
def process_long_for_animal(a):
    meta = generate_facts_script(a.get('name'))
    # For safety in CI we require clips to exist; if none, raise to prevent empty upload
    clips = fetch_clips_for_animal(a)
    if not clips:
        raise RuntimeError('No clips found for '+a.get('name'))
    voice = generate_voice_with_failover(meta['script'])
    music = pick_music()
    out = assemble_long_video(clips, voice_path=voice, music_path=music, title_text=meta.get('title'))
    return upload_video(out, meta.get('title'), meta.get('description'), tags=meta.get('tags'))
if __name__ == '__main__':
    animals = pick_n_unique(7)
    # produce 2 longs + 5 shorts
    for i in range(2):
        try:
            res = process_long_for_animal(animals[i])
            print('Long uploaded:', res)
        except Exception as e:
            print('Long failed:', e)
    # shorts: simple loop (requires clips)
    for sa in pick_n_unique(5):
        try:
            print('Short processing skipped in this build (requires clips)')
        except Exception as e:
            print('Short failed:', e)
