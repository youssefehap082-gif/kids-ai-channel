#!/usr/bin/env python3
import json, sys
from pathlib import Path
from scripts.fetch_wikipedia import build_db
from scripts.utils import get_clips
from scripts.voice_generator import generate_voice_with_failover
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.youtube_uploader import upload_video, upload_captions

DATA = Path(__file__).resolve().parent.parent / 'data'
DB = DATA / 'animal_database.json'

def run_first_run():
    if not DB.exists():
        print('Building animal DB...')
        build_db(DATA / 'animal_list.txt', DB)
    db = json.loads(DB.read_text(encoding='utf-8'))
    if not db:
        raise RuntimeError('No animals in DB')
    animal = db[0]['name']
    print('Selected first animal:', animal)
    clips = get_clips(animal)
    if not clips:
        raise RuntimeError(f'No clips found for {animal}. Enable PEXELS/PIXABAY keys or add local assets.')
    text = db[0].get('summary','Quick facts about '+animal) + ' Don\'t forget to subscribe and hit the bell for more!'
    voice = generate_voice_with_failover(text, preferred_gender='male')
    music = 'assets/music/background.wav'
    watermark = 'assets/watermark.png'
    long_video = assemble_long_video(clips, voice_path=voice, music_path=music, title_text=f"10 Facts About {animal}", watermark_path=watermark)
    short_video = assemble_short(clips, voice_path=voice, music_path=music, watermark_path=watermark, voice_duration=15, max_duration=60)
    # Upload (production)
    resp = upload_video(long_video, f"10 Facts About {animal}", 'Watch 10 amazing facts.', tags=[animal,'facts','animals'], privacyStatus='public')
    vid_id = resp.get('id') if isinstance(resp, dict) else None
    if vid_id:
        print('Uploaded long video id:', vid_id)
        # optional captions upload (make a simple srt)
        try:
            from tools.subtitles import write_simple_srt
            lines = db[0].get('summary','').split('. ')
            srt = '/tmp/captions.srt'
            write_simple_srt(lines, srt, start_offset=0.5, line_duration=4.0)
            upload_captions(vid_id, srt, language='en', is_draft=False)
        except Exception as e:
            print('Caption upload failed:', e)
    # upload short as well
    resp2 = upload_video(short_video, f"{animal} Fact", 'Quick fact short.', tags=[animal,'shorts'], privacyStatus='public')
    print('Uploaded short response:', resp2)
    print('First run complete.')

if __name__ == '__main__':
    run_first_run()
