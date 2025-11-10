import os
from src.youtube import upload_video
from datetime import datetime
import glob

def main():
    # نبحث عن أحدث فيديو قصير
    short_videos = glob.glob("/tmp/**/*.mp4", recursive=True)
    if not short_videos:
        print("❌ No short videos found to upload.")
        return

    latest_short = max(short_videos, key=os.path.getctime)
    print(f"🎥 Found latest short: {latest_short}")

    # بيانات الفيديو القصير
    title = "Amazing Animal Moments #Shorts 🐾"
    description = "Daily wildlife short by WildFacts Hub — Subscribe for more!"
    tags = ["Shorts", "Wildlife", "Animals"]

    # نرفع الفيديو فوراً
    print("🚀 Uploading short directly...")
    upload_id = upload_video(latest_short, title, description, tags, privacy="public")

    if upload_id:
        print(f"✅ Successfully uploaded short! Video ID: {upload_id}")
    else:
        print("❌ Upload failed — check your YouTube token or API permissions.")

if __name__ == "__main__":
    main()
