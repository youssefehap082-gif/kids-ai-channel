#!/usr/bin/env python3
import os, requests
from pathlib import Path
TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def fetch_from_pexels(query, per_page=3):
    key = os.getenv('PEXELS_API_KEY')
    clips = []
    if not key:
        return clips
    headers = {'Authorization': key}
    r = requests.get(f'https://api.pexels.com/videos/search?query={query}&per_page={per_page}', headers=headers, timeout=30)
    r.raise_for_status()
    for v in r.json().get('videos', [])[:per_page]:
        url = v['video_files'][0]['link']
        dest = TMP / (query.replace(' ','_') + '_' + str(len(clips)) + '.mp4')
        r2 = requests.get(url, stream=True, timeout=30)
        with open(dest, 'wb') as f:
            for chunk in r2.iter_content(1024*32):
                f.write(chunk)
        clips.append(str(dest))
    return clips

def fetch_from_pixabay(query, per_page=3):
    key = os.getenv('PIXABAY_API_KEY')
    clips = []
    if not key:
        return clips
    r = requests.get(f'https://pixabay.com/api/videos/?key={key}&q={query}&per_page={per_page}', timeout=30)
    r.raise_for_status()
    for v in r.json().get('hits', [])[:per_page]:
        url = v['videos']['large']['url']
        dest = TMP / (query.replace(' ','_') + '_pix_' + str(len(clips)) + '.mp4')
        r2 = requests.get(url, stream=True, timeout=30)
        with open(dest, 'wb') as f:
            for chunk in r2.iter_content(1024*32):
                f.write(chunk)
        clips.append(str(dest))
    return clips

def fetch_clips_best(query):
    clips = fetch_from_pexels(query, per_page=3)
    if len(clips) < 2:
        clips += fetch_from_pixabay(query, per_page=3)
    return clips
