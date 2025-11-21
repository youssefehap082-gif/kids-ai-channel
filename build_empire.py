import os
import json

# ==========================================
# PHASE 5: LONG FORM + THUMBNAILS + SMART LOGIC
# ==========================================

PROJECT_NAME = "." 

def create_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Updated: {path}")

def main():
    print("🚀 INSTALLING PHASE 5 (THE EMPIRE UPDATE)...")

    # 1. CONTENT ENGINE (Smart: Long vs Short)
    content_engine = """
import random

def generate_script(animal_name, mode="short"):
    print(f"📝 Writing Script ({mode} mode) for: {animal_name}")
    
    # قاعدة بيانات بسيطة (يمكن توسيعها لاحقاً)
    facts_db = [
        f"{animal_name} can sleep for 12 hours straight.",
        f"They have a unique way of communicating.",
        f"Baby {animal_name}s are called cubs or pups.",
        f"They are found mostly in specific jungles.",
        f"Their diet consists mainly of specialized food.",
        f"They are excellent swimmers.",
        f"The {animal_name} population is considered endangered in some areas."
    ]
    random.shuffle(facts_db)
    
    if mode == "long":
        # فيديو طويل: 5-7 حقائق + مقدمة وخاتمة أطول
        selected_facts = facts_db[:6]
        script_text = f"Welcome to our deep dive into the world of the {animal_name}. This creature is truly fascinating. Here are the top amazing facts. {'. '.join(selected_facts)}. Thank you for watching this documentary about the {animal_name}. Don't forget to like and subscribe!"
        title = f"10 Amazing Facts About The {animal_name} 🌍 (Documentary)"
        desc = f"Learn everything about the {animal_name} in this video.\\n#animals #wildlife #documentary #{animal_name.replace(' ', '')}"
    else:
        # شورتس: 3 حقائق سريعة
        selected_facts = facts_db[:3]
        script_text = f"Did you know this about the {animal_name}? {selected_facts[0]}. {selected_facts[1]}. {selected_facts[2]}. Subscribe for more!"
        title = f"{animal_name} Facts in 30 Seconds 😱 #shorts"
        desc = f"Quick facts about {animal_name} #shorts #animals"

    return {
        "title": title,
        "description": desc,
        "script_text": script_text,
        "tags": ["animals", "wildlife", "nature", animal_name]
    }
"""
    create_file("scripts/content_engine.py", content_engine)

    # 2. MEDIA ENGINE (Landscape/Portrait + Thumbnails)
    media_engine = """
import os
import requests

def gather_media(query, orientation="portrait"):
    print(f"🎥 Searching Pexels for: {query} ({orientation})")
    key = os.environ.get("PEXELS_API_KEY")
    if not key: return []
    
    headers = {'Authorization': key}
    # لو طويل هات Landscape، لو شورت هات Portrait
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation={orientation}"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        links = []
        for video in data.get('videos', []):
            files = video.get('video_files', [])
            best = sorted(files, key=lambda x: x['width'] * x['height'], reverse=True)[0]
            links.append(best['link'])
        return links
    except Exception as e:
        print(f"❌ Pexels Error: {e}")
        return []

def get_thumbnail_image(query, output_path="assets/temp/thumb_bg.jpg"):
    print(f"🖼️ Downloading Thumbnail Image for: {query}")
    key = os.environ.get("PEXELS_API_KEY")
    headers = {'Authorization': key}
    # نجيب صورة بالعرض دايماً للثامبنيل
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=landscape"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if data.get('photos'):
            img_url = data['photos'][0]['src']['large2x']
            
            img_data = requests.get(img_url).content
            with open(output_path, 'wb') as f:
                f.write(img_data)
            return output_path
    except:
        pass
    return None

def download_video(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
    return filename
"""
    create_file("scripts/media_engine.py", media_engine)

    # 3. EDITOR ENGINE (Auto-Thumbnail + Logic)
    editor_engine = """
import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

# دالة لعمل الثامبنيل (كتابة على الصورة)
def create_thumbnail(image_path, text, output_path="assets/temp/final_thumb.jpg"):
    try:
        img = Image.open(image_path)
        # تعتيم الصورة شوية عشان الكتابة تبان
        img = img.point(lambda p: p * 0.7)
        
        draw = ImageDraw.Draw(img)
        
        # محاولة تحميل خط، لو مش موجود نستخدم الافتراضي
        try:
            # خط عريض لو متاح في اللينكس
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()

        # كتابة العنوان في النص
        # (تجاوزنا تعقيد توسيط النص للكود البسيط)
        draw.text((50, 50), text, font=font, fill=(255, 255, 0)) # أصفر
        
        img.save(output_path)
        print("✅ Thumbnail Created.")
        return output_path
    except Exception as e:
        print(f"⚠️ Thumbnail Gen Failed: {e}")
        return None

def create_video(video_paths, audio_path, music_path=None, mode="short", output_path="assets/final_video.mp4"):
    print(f"🎬 Editing Video (Mode: {mode})...")
    
    try:
        voice_audio = AudioFileClip(audio_path)
        target_duration = voice_audio.duration + 2
        
        clips = []
        current_duration = 0
        
        # أبعاد الفيديو حسب النوع
        target_w = 1920 if mode == "long" else 1080
        target_h = 1080 if mode == "long" else 1920
        
        while current_duration < target_duration:
            for path in video_paths:
                try:
                    clip = VideoFileClip(path)
                    
                    # Resize Logic
                    # لو الفيديو المصدر مش نفس النسبة، نعمل Crop
                    # للتبسيط هنا بنعمل resize مباشر مع crop center
                    if mode == "short":
                         if clip.h != 1920: clip = clip.resize(height=1920)
                         clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
                    else:
                         # Long Mode (Landscape)
                         if clip.w != 1920: clip = clip.resize(width=1920)
                         clip = clip.crop(x1=0, y1=clip.h/2 - 540, width=1920, height=1080)

                    clips.append(clip)
                    current_duration += clip.duration
                    if current_duration >= target_duration: break
                except: continue
        
        if not clips: return None

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.subclip(0, target_duration)
        
        # Audio Mix
        final_audio = voice_audio
        if music_path and os.path.exists(music_path):
            try:
                music = AudioFileClip(music_path)
                if music.duration < target_duration:
                    music = music.loop(duration=target_duration)
                else:
                    music = music.subclip(0, target_duration)
                music = music.volumex(0.1)
                final_audio = CompositeAudioClip([voice_audio, music])
            except: pass

        final_clip = final_clip.set_audio(final_audio)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=2, preset='ultrafast')
        
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        return None
"""
    create_file("scripts/editor_engine.py", editor_engine)

    # 4. UPLOADER ENGINE (Supports Thumbnails)
    uploader_engine = """
import os
import sys
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.oauth2.credentials import Credentials

def upload_video(file_path, title, description, tags, thumbnail_path=None):
    print("🚀 Uploading to YouTube...")
    
    if not os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        print("❌ Error: Missing Refresh Token")
        return None

    token_info = {
        "client_id": os.environ.get("YOUTUBE_CLIENT_ID"),
        "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET"),
        "refresh_token": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token"
    }

    try:
        creds = Credentials.from_authorized_user_info(token_info)
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "15"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(file_path)
        )
        response = request.execute()
        video_id = response['id']
        print(f"✅ Video Uploaded: {video_id}")

        # Upload Thumbnail if exists
        if thumbnail_path and os.path.exists(thumbnail_path):
            print("🖼️ Uploading Thumbnail...")
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=googleapiclient.http.MediaFileUpload(thumbnail_path)
                ).execute()
                print("✅ Thumbnail Set.")
            except Exception as e:
                print(f"⚠️ Thumbnail Upload Failed: {e}")

        return video_id

    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        return None
"""
    create_file("scripts/uploader_engine.py", uploader_engine)

    # 5. MAIN PIPELINE (The Brain)
    main_pipeline = """
import os
import sys
import json
import random
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video, get_thumbnail_image
from voice_engine import generate_voice
from editor_engine import create_video, create_thumbnail
from uploader_engine import upload_video

def get_random_animal():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'animals_list.json')
        with open(config_path, 'r') as f:
            data = json.load(f)
        categories = list(data['categories'].keys())
        random_cat = random.choice(categories)
        return random.choice(data['categories'][random_cat])
    except:
        return "Lion"

def run_pipeline():
    print("🏁 Starting PHASE 5 Pipeline...")

    # --- SMART DECISION ---
    # لو الساعة دلوقتي 12 UTC (وقت الذروة)، نعمل فيديو طويل
    # غير كدة نعمل Shorts
    current_hour = datetime.datetime.utcnow().hour
    if current_hour == 12:
        mode = "long"
        orientation = "landscape"
        print("🕰️ It's 12:00 UTC! Time for a LONG VIDEO (Documentary Mode).")
    else:
        mode = "short"
        orientation = "portrait"
        print(f"🕰️ It's {current_hour}:00 UTC. Making a SHORT.")
    # -----------------------
    
    animal = get_random_animal()
    script_data = generate_script(animal, mode=mode)
    
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: sys.exit(1)

    local_music = "background.mp3"
    music_path = local_music if os.path.exists(local_music) else None

    # Media
    video_urls = gather_media(animal, orientation=orientation)
    if not video_urls: sys.exit(1)

    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except: pass
    
    if not local_videos: sys.exit(1)

    # Edit
    final_video = create_video(local_videos, audio_path, music_path, mode=mode)
    if not final_video: sys.exit(1)

    # Thumbnail (Only for Long videos)
    thumb_path = None
    if mode == "long":
        raw_thumb = get_thumbnail_image(animal)
        if raw_thumb:
            thumb_path = create_thumbnail(raw_thumb, f"{animal} FACTS")

    # Upload
    video_id = upload_video(
        final_video, 
        script_data['title'], 
        script_data['description'], 
        script_data['tags'],
        thumb_path
    )
    
    if not video_id: sys.exit(1)
    print(f"🎉 DONE! Mode: {mode} | ID: {video_id}")

if __name__ == "__main__":
    run_pipeline()
"""
    create_file("scripts/main_pipeline.py", main_pipeline)

    # 6. Update Requirements (Add Pillow)
    reqs = """
moviepy==1.0.3
requests
google-api-python-client
google-auth-oauthlib
gTTS
imageio-ffmpeg
Pillow
"""
    create_file("requirements.txt", reqs)

    print("\n👑 EMPIRE UPDATE INSTALLED. LONG VIDEOS & THUMBNAILS READY.")

if __name__ == "__main__":
    main()
