import os
import requests

def gather_media(query, orientation="portrait"):
    print(f"🎥 Searching Pexels for: {query} ({orientation})")
    key = os.environ.get("PEXELS_API_KEY")
    if not key: 
        print("⚠️ No Pexels API Key found")
        return []
    
    headers = {'Authorization': key}
    # لو الفيديو طويل هات Landscape، لو شورت هات Portrait
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation={orientation}"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"❌ Pexels Error: {r.text}")
            return []
            
        data = r.json()
        links = []
        for video in data.get('videos', []):
            files = video.get('video_files', [])
            # نختار أعلى جودة
            if files:
                best = sorted(files, key=lambda x: x['width'] * x['height'], reverse=True)[0]
                links.append(best['link'])
        return links
    except Exception as e:
        print(f"❌ Pexels Connection Error: {e}")
        return []

# --- دي الدالة اللي كانت ناقصة وعملت المشكلة ---
def get_thumbnail_image(query, output_path="assets/temp/thumb_bg.jpg"):
    print(f"🖼️ Searching Pexels for Image: {query}")
    key = os.environ.get("PEXELS_API_KEY")
    if not key: return None
    
    headers = {'Authorization': key}
    # دايماً بنجيب صورة بالعرض (Landscape) للثامبنيل
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=landscape"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if data.get('photos'):
            img_url = data['photos'][0]['src']['large2x']
            
            # تحميل الصورة
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img_data = requests.get(img_url).content
            with open(output_path, 'wb') as f:
                f.write(img_data)
            print("✅ Thumbnail Image Downloaded.")
            return output_path
    except Exception as e:
        print(f"⚠️ Failed to get thumbnail image: {e}")
        pass
    return None

def download_video(url, filename):
    try:
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        return filename
    except Exception as e:
        print(f"❌ Download Error: {e}")
        return None
