import os, glob
from datetime import datetime
from src.youtube import upload_video

def find_latest_mp4():
    vids = glob.glob("/tmp/**/*.mp4", recursive=True)
    return max(vids, key=os.path.getctime) if vids else None

def make_test_clip(path="/tmp/test_long.mp4"):
    # كليب صامت 5 ثواني 1280x720 – كفاية للتجربة
    from moviepy.editor import ColorClip
    clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=5)
    clip.write_videofile(path, fps=24, codec="libx264", audio=False, verbose=False, logger=None)
    return path

def main():
    mp4 = find_latest_mp4()
    if not mp4:
        print("⚠️ No long video found, creating a quick test clip...")
        mp4 = make_test_clip()

    title = f"WildFacts Hub — Test Long Upload {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    desc = "Automatic test upload (long). If you can see this, YouTube auth is OK."
    tags = ["Wildlife", "Nature", "Animals"]

    print("🚀 Uploading LONG video now (no schedule)...")
    upload_video(mp4, title, desc, tags, privacy="public", schedule_time_rfc3339=None)

if __name__ == "__main__":
    main()
