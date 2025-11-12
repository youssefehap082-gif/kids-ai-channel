import os
import random
import requests
from moviepy.editor import ImageSequenceClip, AudioFileClip
from youtube import upload_video

animals = ["Lion", "Tiger", "Monkey", "Panda", "Elephant", "Wolf", "Eagle"]
animal = random.choice(animals)
print(f"🎬 Creating short for {animal}")

# 🖼️ تحميل صور من Pexels
PEXELS_API = os.environ.get("PEXELS_API_KEY")
headers = {"Authorization": PEXELS_API}
res = requests.get(f"https://api.pexels.com/v1/search?query={animal}&per_page=5", headers=headers).json()
images = [photo["src"]["medium"] for photo in res["photos"]]

os.makedirs("frames", exist_ok=True)
for idx, url in enumerate(images):
    img_data = requests.get(url).content
    with open(f"frames/frame{idx}.jpg", "wb") as f:
        f.write(img_data)

# 🧩 موسيقى خلفية مجانية (ملف ثابت)
music_url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Scott_Holmes_Music/Happy_Music/Scott_Holmes_Music_-_Happy_Whistle.mp3"
music_path = "music.mp3"
if not os.path.exists(music_path):
    open(music_path, "wb").write(requests.get(music_url).content)

clip = ImageSequenceClip(["frames/" + f for f in os.listdir("frames")], fps=1)
audio = AudioFileClip(music_path).volumex(0.3)
final_video = clip.set_audio(audio)
file_name = f"{animal.lower()}_short.mp4"
final_video.write_videofile(file_name, fps=24)

# 🧠 تحسينات الـ SEO
title = f"{animal} In Action 🐾 | AI Wildlife Short #Shorts"
description = f"Watch this relaxing AI short of the {animal} with music. Subscribe for more 🐾 #wildlife #animals #shorts"
tags = [animal.lower(), "shorts", "wildlife", "AI", "nature", "animals"]

print("🚀 Uploading short...")
upload_video(file_name, title, description, tags)
