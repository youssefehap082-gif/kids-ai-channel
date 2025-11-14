import os, random, time
from pathlib import Path
from scripts.init import *
from scripts.animal_selector import pick_n_unique
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import generate_voice_with_failover
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.youtube_uploader import upload_video
from scripts.utils import download_file
TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

PEXELS = os.getenv('PEXELS_API_KEY')
PIXABAY = os.getenv('PIXABAY_API_KEY')

def fetch_clips_for_animal(animal, max_clips=4):
    clips = []
    q = animal.get('video_search_terms', [animal['name']])[0]
    # Pexels
    if PEXELS:
        try:
            import requests
            headers = {'Authorization': PEXELS}
            r = requests.get(f'https://api.pexels.com/videos/search?query={q}&per_page=8', headers=headers, timeout=30)
            for v in r.json().get('videos', [])[:6]:
                files = v.get('video_files', [])
                if files:
                    url = files[0].get('link')
                    if url:
                        dest = TMP / f"{animal['name']}_pex_{len(clips)}.mp4"
                        download_file(url, dest)
                        clips.append(dest)
                        if len(clips)>=max_clips: break
        except Exception:
            pass
    # Pixabay fallback
    if PIXABAY and len(clips)<max_clips:
        try:
            import requests
            r = requests.get(f'https://pixabay.com/api/videos/?key={PIXABAY}&q={q}&per_page=8', timeout=30)
            for v in r.json().get('hits', [])[:6]:
                url = v.get('videos', {}).get('large', {}).get('url')
                if url:
                    dest = TMP / f"{animal['name']}_pix_{len(clips)}.mp4"
                    download_file(url, dest)
                    clips.append(dest)
                    if len(clips)>=max_clips: break
        except Exception:
            pass
    return clips

def pick_music_for_short():
    music_folder = Path(__file__).resolve().parent.parent / 'assets' / 'music'
    files = list(music_folder.glob('*.mp3')) if music_folder.exists() else []
    return files[0] if files else None

def process_long_for_animal(animal, sex='male'):
    meta = generate_facts_script(animal['name'])
    clips = fetch_clips_for_animal(animal)
    if not clips:
        raise RuntimeError('No clips found for '+animal['name'])
    script_text = meta['script'] + "\n\nDon't forget to subscribe and hit the bell for more!"
    voice = generate_voice_with_failover(script_text, preferred_gender= 'male' if sex=='male' else 'female')
    music = pick_music_for_short()
    out = assemble_long_video(clips, voice, music_path=music, title_text=meta['title'])
    uploaded = upload_video(out, meta['title'], meta['description'], tags=meta['tags'])
    return uploaded

def process_short_for_animal(animal):
    clips = fetch_clips_for_animal(animal, max_clips=1)
    if not clips:
        raise RuntimeError('No clips for short '+animal['name'])
    music = pick_music_for_short()
    out = assemble_short(clips[0], music)
    title = f"{animal['name'].title()} — Short"
    desc = f"Short clip of {animal['name']}\n#shorts #{animal['name']}"
    uploaded = upload_video(out, title, desc, tags=[animal['name'], 'shorts'])
    return uploaded

if __name__ == '__main__':
    TEST = os.getenv('TEST_RUN', 'true').lower() == 'true'
    # determine counts
    if TEST:
        longs = 1; shorts = 1
    else:
        longs = 2; shorts = 5
    animals = pick_n_unique(longs + shorts)
    sexes = ['male','female']
    uploaded = []
    # longs
    for i in range(longs):
        try:
            res = process_long_for_animal(animals[i], sex=sexes[i%2])
            uploaded.append(res)
        except Exception as e:
            print('Long failed for', animals[i]['name'], str(e))
    # shorts
    for j in range(shorts):
        try:
            idx = longs + j
            if idx >= len(animals):
                # pick another
                a = pick_n_unique(1)[0]
            else:
                a = animals[idx]
            uploaded.append(process_short_for_animal(a))
        except Exception as e:
            print('Short failed for', str(e))
    print('Uploaded:', uploaded)
