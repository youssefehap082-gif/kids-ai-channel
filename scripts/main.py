import os, time, random
from scripts.init import *
from scripts.animal_selector import pick_n_unique
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import generate_voice_with_failover
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.youtube_uploader import upload_video
from scripts.ai_optimizer import update_performance_data
from pathlib import Path
TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def fetch_clips_for_animal(animal):
    import requests
    from scripts.utils import download_file
    clips = []
    pkey = os.getenv('PEXELS_API_KEY')
    pix = os.getenv('PIXABAY_API_KEY')
    q = animal.get('video_search_terms',[animal['name']])[0]
    if pkey:
        try:
            r = requests.get(f'https://api.pexels.com/videos/search?query={q}&per_page=8', headers={'Authorization':pkey}, timeout=30)
            for v in r.json().get('videos',[])[:6]:
                url = v['video_files'][0]['link']
                dest = TMP / f"{animal['name']}_{len(clips)}.mp4"
                download_file(url,dest)
                clips.append(dest)
                if len(clips)>=4: break
        except Exception as e:
            print('Pexels error', e)
    if pix and len(clips)<2:
        try:
            r = requests.get(f'https://pixabay.com/api/videos/?key={pix}&q={q}&per_page=8', timeout=30)
            for v in r.json().get('hits',[])[:6]:
                url = v['videos']['large']['url']
                dest = TMP / f"{animal['name']}_pix_{len(clips)}.mp4"
                download_file(url,dest)
                clips.append(dest)
                if len(clips)>=4: break
        except Exception as e:
            print('Pixabay error', e)
    if not clips:
        raise RuntimeError('NO CLIPS')
    return clips

def pick_music_for_short():
    folder = Path(__file__).resolve().parent.parent / 'assets' / 'music'
    files = list(folder.glob('*.mp3'))
    return files[0] if files else None

def process_long_for_animal(animal, sex='male'):
    meta = generate_facts_script(animal['name'])
    clips = fetch_clips_for_animal(animal)
    script_text = meta['script'] + "\n\nDon't forget to subscribe and hit the bell for more!"
    voice = generate_voice_with_failover(script_text, preferred_gender='male' if sex=='male' else 'female')
    music = pick_music_for_short()
    out = assemble_long_video(clips, voice, music_path=music, title_text=meta['title'])
    vid = upload_video(out, meta['title'], meta['description'], meta.get('tags'))
    if not vid:
        raise RuntimeError('Upload failed for long')
    try:
        update_performance_data([{'video_id':vid,'animal_name':animal['name']}])
    except Exception as e:
        print('Perf update failed', e)
    return vid

def process_short_for_animal(animal):
    clips = fetch_clips_for_animal(animal)
    music = pick_music_for_short()
    out = assemble_short(clips[0], music)
    title = f"{animal['name'].title()} — Short"
    desc = f"Short clip of {animal['name']}\n#shorts #{animal['name']}"
    vid = upload_video(out, title, desc, tags=[animal['name'],'shorts'])
    if not vid:
        raise RuntimeError('Upload failed for short')
    try:
        update_performance_data([{'video_id':vid,'animal_name':animal['name']}])
    except Exception as e:
        print('Perf update failed', e)
    return vid

if __name__ == '__main__':
    animals = pick_n_unique(7)
    sexes = ['male','female']
    for i in range(2):
        process_long_for_animal(animals[i], sex=sexes[i%2])
        time.sleep(2)
    for a in animals[2:7]:
        process_short_for_animal(a)
        time.sleep(1)
    print('DONE')
