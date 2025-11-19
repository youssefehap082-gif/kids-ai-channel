import requests
import os
from scripts.utils import http

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def get_assets(topic, script_data):
    assets = []
    for segment in script_data['segments']:
        query = segment['keywords'][0]
        file_path = _fetch_pexels_video(query)
        if not file_path:
            file_path = _fetch_pixabay_fallback(query)
        assets.append({"text": segment['text'], "video": file_path})
    return assets

def _fetch_pexels_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=landscape"
    resp = http.fetch_with_retry(url, headers=headers)
    
    if resp and resp.json().get('videos'):
        video_url = resp.json()['videos'][0]['video_files'][0]['link']
        return _download_file(video_url)
    return None

def _fetch_pixabay_fallback(query):
    # Placeholder for Pixabay logic
    return "data/defaults/default_bg.mp4"

def _download_file(url):
    local_filename = f"data/temp/{abs(hash(url))}.mp4"
    os.makedirs("data/temp", exist_ok=True)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename
