import os
import sys
# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video
from voice_engine import generate_voice
from editor_engine import create_video
from uploader_engine import upload_video

def run_pipeline():
    print("🏁 Starting PRODUCTION Pipeline (STRICT)...")
    
    # 1. Topic
    animal = "Red Panda"
    
    # 2. Script
    script_data = generate_script(animal)
    
    # 3. Voice
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: sys.exit(1) # وقف لو الصوت فشل

    # 4. Media
    video_urls = gather_media(animal)
    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    
    if not video_urls:
        print("❌ No videos found on Pexels!")
        sys.exit(1)

    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except:
            pass
    
    if not local_videos: 
        print("❌ Failed to download any videos.")
        sys.exit(1)

    # 5. Edit
    final_video = create_video(local_videos, audio_path)
    if not final_video: 
        print("❌ Editing Failed.")
        sys.exit(1)

    # 6. Upload (اللحظة الحاسمة)
    video_id = upload_video(final_video, script_data['title'], script_data['description'])
    
    if not video_id:
        print("❌ Upload return no ID. Failing pipeline.")
        sys.exit(1)
    
    print("🎉🎉🎉 VIDEO IS ACTUALLY ON YOUTUBE NOW!")

if __name__ == "__main__":
    run_pipeline()
