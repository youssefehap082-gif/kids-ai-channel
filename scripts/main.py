# main.py - orchestrator (updated)
import os
from pathlib import Path
import random
from scripts.init import *
from scripts.animal_selector import pick_n_unique
from scripts.content_generator import generate_facts_script
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.youtube_uploader import upload_video, get_youtube_service
from scripts import video_classifier, captions_uploader, captions_aligner, ai_optimizer
from scripts.voice_generator import generate_voice_with_failover
from scripts.utils import download_file
import requests
import time

TEST = os.getenv('TEST_RUN', 'true').lower() == 'true'
TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def pick_music_for_short():
    music_folder = Path(__file__).resolve().parent.parent / 'assets' / 'music'
    files = list(music_folder.glob('*.mp3'))
    return files[0] if files else None

def fetch_clips_for_animal(animal, max_clips=4):
    clips = []
    pkey = os.getenv('PEXELSAPIKEY')
    pix_key = os.getenv('PIXABAYAPIKEY')
    q = animal.get('video_search_terms', [animal['name']])[0]
    if pkey:
        try:
            headers = {'Authorization': pkey}
            r = requests.get(f'https://api.pexels.com/videos/search?query={q}&per_page=8', headers=headers, timeout=30)
            for v in r.json().get('videos', [])[:6]:
                try:
                    url = v['video_files'][0]['link']
                    dest = TMP / f"{animal['name']}_{len(clips)}.mp4"
                    download_file(url, dest)
                    ok = video_classifier.verify_clip_contains_animal(dest, animal['name'])
                    if ok:
                        clips.append(dest)
                    else:
                        try:
                            dest.unlink(missing_ok=True)
                        except Exception:
                            pass
                    if len(clips) >= max_clips:
                        break
                except Exception:
                    continue
        except Exception as e:
            print("Pexels fetch error:", e)
    if pix_key and len(clips) < max_clips:
        try:
            r = requests.get(f'https://pixabay.com/api/videos/?key={pix_key}&q={q}&per_page=8', timeout=30)
            for v in r.json().get('hits', [])[:6]:
                try:
                    url = v['videos']['large']['url']
                    dest = TMP / f"{animal['name']}_pix_{len(clips)}.mp4"
                    download_file(url, dest)
                    ok = video_classifier.verify_clip_contains_animal(dest, animal['name'])
                    if ok:
                        clips.append(dest)
                    else:
                        try:
                            dest.unlink(missing_ok=True)
                        except Exception:
                            pass
                    if len(clips) >= max_clips:
                        break
                except Exception:
                    continue
        except Exception as e:
            print("Pixabay fetch error:", e)
    return clips

def process_long_for_animal(animal, sex='male'):
    meta = generate_facts_script(animal['name'])
    clips = fetch_clips_for_animal(animal, max_clips=4)
    if not clips:
        print("No verified clips for", animal['name'])
        return None
    script_text = meta['script'] + "\n\nDon't forget to subscribe and hit the bell for more!"
    try:
        voice_path = generate_voice_with_failover(script_text, preferred_gender= 'male' if sex=='male' else 'female')
    except Exception as e:
        print("TTS failed for", animal['name'], ":", e)
        voice_path = None
    music = pick_music_for_short()
    out = assemble_long_video(clips, voice_path, music_path=music, title_text=meta['title'])
    try:
        uploaded = upload_video(out, meta['title'], meta['description'], tags=meta['tags'], is_short=False)
    except Exception as e:
        print("Upload failed:", e)
        uploaded = None
    try:
        duration = 180.0
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(str(out))
            duration = clip.duration
            try:
                clip.reader.close()
            except Exception:
                pass
        except Exception:
            pass
        srt_path = TMP / f"{animal['name']}_{int(time.time())}.srt"
        # use forced-alignment if possible
        if voice_path:
            captions_file = captions_aligner.generate_best_srt(script_text, voice_path, srt_path, duration, lang='eng')
        else:
            captions_file = captions_uploader.create_srt_from_script(script_text, duration, srt_path)
        # upload captions automatically if you want (requires YouTube scopes)
        try:
            if uploaded and uploaded.get('id'):
                yt = get_youtube_service()
                captions_uploader.upload_srt_to_youtube(yt, uploaded.get('id'), captions_file)
        except Exception as e:
            print('Auto caption upload failed (check scopes):', e)
    except Exception as e:
        print("Captions creation failed:", e)
    try:
        if uploaded and uploaded.get('id'):
            ai_optimizer.update_performance_data([{'video_id': uploaded.get('id'), 'animal_name': animal['name']}])
    except Exception as e:
        print("AI optimizer update failed:", e)
    return uploaded

def process_short_for_animal(animal):
    clips = fetch_clips_for_animal(animal, max_clips=2)
    if not clips:
        print("No clips for short:", animal['name'])
        return None
    music = pick_music_for_short()
    out = assemble_short(clips[0], music)
    title = f"{animal['name'].title()} — Short"
    desc = f"Short clip of {animal['name']}\n#shorts #{animal['name']}"
    try:
        uploaded = upload_video(out, title, desc, tags=[animal['name'], 'shorts'], is_short=True)
    except Exception as e:
        print("Short upload failed:", e)
        uploaded = None
    try:
        if uploaded and uploaded.get('id'):
            ai_optimizer.update_performance_data([{'video_id': uploaded.get('id'), 'animal_name': animal['name']}])
    except Exception as e:
        print("AI optimizer update failed for short:", e)
    return uploaded

if __name__ == '__main__':
    animals = pick_n_unique(7) if not TEST else pick_n_unique(3)
    print("Selected animals:", [a['name'] for a in animals])
    sexes = ['male', 'female']
    if TEST:
        print("TEST RUN: uploading 1 long + 1 short")
        long_res = process_long_for_animal(animals[0], sex=sexes[0])
        short_res = process_short_for_animal(animals[1])
        print("Test uploaded:", long_res, short_res)
    else:
        uploaded = []
        for i in range(2):
            uploaded.append(process_long_for_animal(animals[i], sex=sexes[i%2]))
            time.sleep(2)
        shorts_animals = animals[2:7]
        for sa in shorts_animals:
            uploaded.append(process_short_for_animal(sa))
            time.sleep(1)
        print("Uploaded:", uploaded)
