import os
from src.media_sources import pick_video_urls
from src.compose import compose_video
from src.youtube import upload_video

def main():
    print("🧠 main_long.py started successfully!")  # ✅ لمتابعة التشغيل

    try:
        topics = ["lion", "elephant", "tiger", "penguin", "panda"]
        for topic in topics[:2]:  # ← هنا بيعمل فيديوهين بس في الرن
            print(f"🎬 Generating long video for: {topic}")
            paths = pick_video_urls(topic)
            final_video = compose_video(paths, voiceover=True)

            title = f"WildFacts Hub - Amazing Facts About {topic.capitalize()}"
            desc = f"Discover wild facts about {topic.capitalize()}! 🐾 #WildFactsHub"
            tags = [topic, "animal facts", "wildlife", "nature"]

            print(f"🚀 Starting upload for: {title}")
            video_id = upload_video(final_video, title, desc, tags, privacy="public")

            if video_id:
                print(f"✅ Upload success! Video ID: {video_id}")
            else:
                print("❌ Upload failed or video_id is None.")

        print("✅ main_long.py finished execution successfully.")

    except Exception as e:
        print(f"💥 Error in main_long.py: {e}")

if __name__ == "__main__":
    main()
