import requests
import os
import logging
from scripts.utils import http

def get_assets(topic, script_data):
    assets = []
    os.makedirs("data/temp", exist_ok=True)
    
    # Default Pexels/Pixabay Fallback videos (Nature)
    FALLBACK_VIDEOS = [
        "https://player.vimeo.com/external/371835693.sd.mp4?s=c321695e4a43c2985153d638261414a02849455d&profile_id=164&oauth2_token_id=57447761",
        "https://player.vimeo.com/external/464518608.sd.mp4?s=97b799c29176f3053169791f5098a3939548a826&profile_id=164&oauth2_token_id=57447761"
    ]

    logging.info(f"Fetching media for topic: {topic}")

    for i, segment in enumerate(script_data['segments']):
        query = segment.get('keywords', [topic])[0]
        video_path = f"data/temp/video_{i}.mp4"
        
        # Try to fetch specific video
        if not _fetch_pexels_video(query, video_path):
            logging.warning(f"Could not fetch video for {query}, using fallback.")
            # Use fallback video
            fallback_url = FALLBACK_VIDEOS[i % len(FALLBACK_VIDEOS)]
            _download_file(fallback_url, video_path)
        
        assets.append({"text": segment['text'], "video": video_path})
    
    return assets

def _fetch_pexels_video(query, save_path):
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key or "***" in api_key:
        return False

    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=landscape&size=medium"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get('videos'):
            video_url = data['videos'][0]['video_files'][0]['link']
            return _download_file(video_url, save_path)
    except Exception as e:
        logging.error(f"Pexels Error: {e}")
    
    return False

def _download_file(url, path):
    try:
        with requests.get(url, stream=True, timeout=20) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return False