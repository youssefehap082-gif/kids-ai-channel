import requests
import os
import logging
import time
import random

def get_assets(topic, script_data):
    assets = []
    os.makedirs("data/temp", exist_ok=True)
    
    logging.info(f"Fetching DIFFERENT clips for {len(script_data['segments'])} segments...")

    used_videos = set()

    for i, segment in enumerate(script_data['segments']):
        query = segment['keywords'][0]
        video_path = f"data/temp/clip_{i}.mp4"
        
        # Try finding a new video
        found = False
        if _fetch_pexels_video(query, video_path, used_ids=used_videos):
            found = True
        
        # Fallback to Pixabay if Pexels fails
        if not found:
             _download_fallback(video_path)

        assets.append({"text": segment['text'], "video": video_path})
        time.sleep(1) # Respect API limits
    
    return assets

def _fetch_pexels_video(query, save_path, used_ids):
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key: return False

    headers = {"Authorization": api_key}
    # Search for 10 videos to pick a random unused one
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=landscape&size=medium"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get('videos'):
            # Pick a video that hasn't been used yet
            for vid in data['videos']:
                if vid['id'] not in used_ids:
                    video_url = vid['video_files'][0]['link']
                    if _download_file(video_url, save_path):
                        used_ids.add(vid['id'])
                        return True
    except Exception as e:
        logging.error(f"Pexels search error: {e}")
    
    return False

def _download_fallback(path):
    # A generic nature background as absolute backup
    url = "https://player.vimeo.com/external/371835693.sd.mp4?s=c321695e4a43c2985153d638261414a02849455d"
    _download_file(url, path)

def _download_file(url, path):
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except:
        return False