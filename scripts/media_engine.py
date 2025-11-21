
import os
import requests
import random

def gather_media(query):
    print(f"🎥 Searching Pexels for: {query}")
    key = os.environ.get("PEXELS_API_KEY")
    if not key: return []
    
    headers = {'Authorization': key}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        links = []
        for video in data.get('videos', []):
            # Get the best quality link
            files = video.get('video_files', [])
            best = sorted(files, key=lambda x: x['width'] * x['height'], reverse=True)[0]
            links.append(best['link'])
        return links
    except Exception as e:
        print(f"❌ Pexels Error: {e}")
        return []

def download_video(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
    return filename
