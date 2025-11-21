
import os
import requests
import random

def search_pexels(query, api_key, per_page=5):
    headers = {'Authorization': api_key}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation=landscape"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return [v['video_files'][0]['link'] for v in r.json()['videos'] if v['video_files']]
    except:
        return []
    return []

def search_pixabay(query, api_key):
    url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}&per_page=5"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return [v['videos']['large']['url'] for v in r.json()['hits']]
    except:
        return []
    return []

def gather_media(animal_name):
    print(f"🎥 Hunting media for: {animal_name}")
    
    pexels_key = os.environ.get("PEXELS_API_KEY")
    pixabay_key = os.environ.get("PIXABAY_API_KEY")
    
    videos = []
    
    # 1. Try Pexels
    if pexels_key:
        videos += search_pexels(animal_name, pexels_key)
        
    # 2. Try Pixabay (Fallback/Addition)
    if pixabay_key and len(videos) < 3:
        videos += search_pixabay(animal_name, pixabay_key)
    
    # Fallback: General animal query if specific fails
    if not videos:
        print("⚠️ Specific search failed, trying general tag...")
        if pexels_key: videos += search_pexels("wildlife", pexels_key)
        
    print(f"✅ Found {len(videos)} videos.")
    return videos[:5] # Return top 5
