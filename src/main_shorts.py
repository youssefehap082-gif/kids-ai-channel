import os
from src.media_sources import pick_video_urls
from src.compose import compose_video
from src.youtube import upload_video

def main():
    print("🧠 main_shorts.py started successfully!")  # ✅ لمتابعة التشغيل

    try:
        topics = ["cat", "dog", "fish", "bird", "lion", "panda"]
        for topic in topics[:6]:  # ← عدد 6 شورتس
            print(f"🎬 Generating short for: {topic}")
            paths = pick_video_urls(topic)
            final_video = compose_video(paths, short=True, voiceover=False)

            title = f"WildFacts Hub Shorts - {topic.capitalize()} Moments 🐾"
            desc = f"Enjoy amazing {topic} videos! #WildFactsHub #Shorts"
            tags = [topic, "animal", "shorts", "wildlife"]

            print(f"🚀 Starting upload for short: {title}")
            video_id = upload_video(final_video, title, desc, tags, privacy="public")

            if video_id:
                print(f"✅ Upload success! Video ID: {video_id}")
            else:
                print("❌ Upload failed or video_id is None.")

        print("✅ main_shorts.py finished execution successfully.")

    except Exception as e:
        print(f"💥 Error in main_shorts.py: {e}")

if __name__ == "__main__":
    main()
