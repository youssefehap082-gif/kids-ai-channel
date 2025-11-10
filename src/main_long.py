import os
from src.youtube import upload_video
from datetime import datetime
import glob

def main():
    # تأكيد المسار المحلي للفيديوهات الجاهزة
    video_files = glob.glob("/tmp/**/*.mp4", recursive=True)
    if not video_files:
        print("❌ No video files found to upload.")
        return

    latest_video = max(video_files, key=os.path.getctime)
    print(f"🎬 Found latest video: {latest_video}")

    # بيانات الفيديو التجريبية
    title = "Test Upload — WildFacts Hub 🦁"
    description = "Automatic test upload from WildFacts Hub system. Stay tuned for daily wildlife videos!"
    tags = ["Wildlife", "Nature", "Animals", "Facts"]

    # رفع الفيديو مباشرة (بدون جدول)
    print("🚀 Uploading video directly...")
    upload_id = upload_video(latest_video, title, description, tags, privacy="public")

    if upload_id:
        print(f"✅ Successfully uploaded! Video ID: {upload_id}")
    else:
        print("❌ Upload failed — check your YouTube API credentials or token.")

if __name__ == "__main__":
    main()
