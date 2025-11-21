import os
import requests
import random

def gather_media(query):
    print(f"🎥 Searching Pexels for: {query}")
    key = os.environ.get("PEXELS_API_KEY")
    if not key: 
        print("⚠️ No Pexels Key found!")
        return []
    
    headers = {'Authorization': key}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        links = []
        for video in data.get('videos', []):
            files = video.get('video_files', [])
            # Get best quality
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

# --- الإضافة الجديدة: تحميل موسيقى خلفية ---
def get_background_music(output_path="assets/temp/background.mp3"):
    print("🎵 Downloading Background Music...")
    # رابط مباشر لموسيقى مجانية (Upbeat Ukulele style)
    music_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    
    if not os.path.exists(output_path):
        try:
            r = requests.get(music_url, stream=True)
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
            print("✅ Music Downloaded.")
        except Exception as e:
            print(f"⚠️ Could not download music: {e}")
            return None
    return output_path
