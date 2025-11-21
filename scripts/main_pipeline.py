
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
