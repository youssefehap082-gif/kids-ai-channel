import os, requests, uuid
from pathlib import Path

PEXELS = os.getenv('PEXELS_API_KEY')
PIX = os.getenv('PIXABAY_API_KEY')

ASSETS = Path(__file__).resolve().parent.parent / 'assets' / 'clips'
ASSETS.mkdir(parents=True, exist_ok=True)

def ensure_local(name):
    folder = ASSETS / name.replace(' ', '_').lower()
    if folder.exists():
        return [str(f) for f in folder.glob('*.mp4')]
    return []

def download_video(url, animal):
    folder = ASSETS / animal.replace(' ', '_').lower()
    folder.mkdir(parents=True, exist_ok=True)
    fname = folder / f"{uuid.uuid4().hex}.mp4"
    try:
        r = requests.get(url, stream=True, timeout=60)
        if r.status_code == 200:
            with open(fname, 'wb') as f:
                for chunk in r.iter_content(1024*1024):
                    f.write(chunk)
            return str(fname)
    except Exception:
        return None
    return None

def fetch_from_pexels(name, max_results=6):
    if not PEXELS:
        return []
    headers = {'Authorization': PEXELS}
    url = f"https://api.pexels.com/videos/search?query={name}&per_page={max_results}"
    r = requests.get(url, headers=headers, timeout=30)
    if not r.ok:
        return []
    vids = []
    for v in r.json().get('videos', []):
        files = v.get('video_files', [])
        if files:
            link = files[0].get('link')
            if link:
                local = download_video(link, name)
                if local:
                    vids.append(local)
    return vids

def fetch_from_pixabay(name, max_results=6):
    if not PIX:
        return []
    q = name.replace(' ', '+')
    url = f"https://pixabay.com/api/videos/?key={PIX}&q={q}&per_page={max_results}"
    r = requests.get(url, timeout=30)
    if not r.ok:
        return []
    vids = []
    for h in r.json().get('hits', []):
        link = h.get('videos', {}).get('medium', {}).get('url')
        if link:
            local = download_video(link, name)
            if local:
                vids.append(local)
    return vids

def get_clips(name):
    local = ensure_local(name)
    if local:
        return local
    clips = fetch_from_pexels(name)
    if len(clips) < 2:
        clips += fetch_from_pixabay(name)
    return clips
