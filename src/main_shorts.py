import os, glob
from datetime import datetime
from src.youtube import upload_video

def find_latest_mp4():
    vids = glob.glob("/tmp/**/*.mp4", recursive=True)
    return max(vids, key=os.path.getctime) if vids else None

def make_test_short(path="/tmp/test_short.mp4"):
    from moviepy.editor import ColorClip
    clip = ColorClip(size=(1080, 1920), color=(10, 90, 10), duration=5)
    clip.write_videofile(path, fps=30, codec="libx264", audio=False, verbose=False, logger=None)
    return path

def main():
    mp4 = find_latest_mp4()
    if not mp4:
        print("⚠️ No short video found, creating a quick test short...")
        mp4 = make_test_short()

    title = f"Amazing Animal Moments #Shorts — Test {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
    desc = "Automatic test upload (short). If you can see this, YouTube auth is OK."
    tags = ["Shorts", "Wildlife", "Animals"]

    print("🚀 Uploading SHORT now (no schedule)...")
    upload_video(mp4, title, desc, tags, privacy="public", schedule_time_rfc3339=None)

if __name__ == "__main__":
    main()
