import os
import json

# ==========================================
# PHASE 3: PRODUCTION & UPLOAD (THE FINAL BOSS)
# ==========================================

PROJECT_NAME = "." 

def create_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Created: {path}")

def main():
    print("🚀 INSTALLING STUDIO & UPLOAD MODULES...")

    # 1. CONTENT ENGINE (REAL AI)
    content_engine = """
import os
import json
from openai import OpenAI

def generate_script(animal_name):
    print(f"📝 Writing Viral Script for: {animal_name}")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: return None
    
    client = OpenAI(api_key=api_key)
    prompt = f'''
    Create a viral YouTube Shorts script about {animal_name}.
    Duration: 30-40 seconds.
    Style: Fast, Shocking, Engaging.
    JSON Format:
    {{
        "title": "Catchy Title Here",
        "description": "SEO description with hashtags",
        "script_text": "Full narration text here..."
    }}
    '''
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Script Error: {e}")
        return {
            "title": f"Amazing Facts about {animal_name}",
            "description": f"#shorts #{animal_name}",
            "script_text": f"Did you know the {animal_name} is one of the most interesting animals? It has unique behaviors that will shock you. Subscribe for more!"
        }
"""
    create_file("scripts/content_engine.py", content_engine)

    # 2. MEDIA ENGINE (REAL PEXELS)
    media_engine = """
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
"""
    create_file("scripts/media_engine.py", media_engine)

    # 3. VOICE ENGINE (REAL TTS)
    voice_engine = """
import os
from openai import OpenAI

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voice...")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: return None
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text
        )
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None
"""
    create_file("scripts/voice_engine.py", voice_engine)

    # 4. EDITOR ENGINE (REAL MOVIEPY)
    editor_engine = """
import os
from moviepy.editor import VideoFileClip, AudioFileClip, ConcatenateVideoClip, vfx

def create_video(video_paths, audio_path, output_path="assets/final_video.mp4"):
    print("🎬 Editing Video...")
    
    try:
        # Load Audio to get duration
        audio = AudioFileClip(audio_path)
        target_duration = audio.duration
        
        clips = []
        current_duration = 0
        
        # Load and loop videos to match audio
        while current_duration < target_duration:
            for path in video_paths:
                clip = VideoFileClip(path)
                # Resize to vertical 9:16 if needed (basic crop)
                clip = clip.resize(height=1920)
                clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
                
                clips.append(clip)
                current_duration += clip.duration
                if current_duration >= target_duration:
                    break
        
        # Concatenate
        final_clip = ConcatenateVideoClip(clips)
        # Trim to audio length
        final_clip = final_clip.subclip(0, target_duration)
        # Add Audio
        final_clip = final_clip.set_audio(audio)
        
        # Export
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        print(f"✅ Video Rendered: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        return None
"""
    create_file("scripts/editor_engine.py", editor_engine)

    # 5. UPLOADER ENGINE (REAL YOUTUBE)
    uploader_engine = """
import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

def upload_video(file_path, title, description):
    print("🚀 Uploading to YouTube...")
    
    # Reconstruct Credentials from Secrets
    token_info = {
        "client_id": os.environ.get("YOUTUBE_CLIENT_ID"),
        "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET"),
        "refresh_token": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    if not all(token_info.values()):
        print("❌ Missing YouTube Keys")
        return None

    try:
        creds = Credentials.from_authorized_user_info(token_info)
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["shorts", "animals", "nature"],
                    "categoryId": "15" # Pets & Animals
                },
                "status": {
                    "privacyStatus": "public", # Changed to PUBLIC for action
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=googleapiclient.http.MediaFileUpload(file_path)
        )
        response = request.execute()
        print(f"✅ Upload Success! Video ID: {response['id']}")
        return response['id']
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        return None
"""
    create_file("scripts/uploader_engine.py", uploader_engine)

    # 6. MAIN PIPELINE (THE CONDUCTOR)
    main_pipeline = """
import os
import sys
import json
# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video
from voice_engine import generate_voice
from editor_engine import create_video
from uploader_engine import upload_video

def run_pipeline():
    print("🏁 Starting PRODUCTION Pipeline...")
    
    # 1. Topic
    animal = "Red Panda" 
    
    # 2. Script
    script_data = generate_script(animal)
    if not script_data: return

    # 3. Voice
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: return

    # 4. Media
    video_urls = gather_media(animal)
    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        download_video(url, path)
        local_videos.append(path)
    
    if not local_videos: 
        print("No videos downloaded")
        return

    # 5. Edit
    final_video = create_video(local_videos, audio_path)
    if not final_video: return

    # 6. Upload
    upload_video(final_video, script_data['title'], script_data['description'])
    
    print("🎉🎉🎉 PIPELINE FINISHED SUCCESSFULLY!")

if __name__ == "__main__":
    run_pipeline()
"""
    create_file("scripts/main_pipeline.py", main_pipeline)

    # 7. WORKFLOW UPDATE (Install ImageMagick)
    workflow = """name: Daily Auto-Tube Pipeline

on:
  workflow_dispatch: # Manual Trigger Only for now

jobs:
  produce_and_upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install System Deps
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg imagemagick ghostscript
          
      - name: Install Python Deps
        run: pip install openai requests google-api-python-client google-auth-oauthlib moviepy==1.0.3 imageio-ffmpeg

      - name: Run Pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          YOUTUBE_CLIENT_ID: ${{ secrets.YT_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YT_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YT_REFRESH_TOKEN }}
        run: python scripts/main_pipeline.py
"""
    create_file(".github/workflows/daily_video.yml", workflow)

    print("\n🎬 STUDIO INSTALLED. READY FOR ACTION.")

if __name__ == "__main__":
    main()