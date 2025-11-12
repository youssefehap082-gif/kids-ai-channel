import os
import random
import requests
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip, TextClip
from youtube import upload_video
import datetime

animals = ["Lion", "Tiger", "Monkey", "Panda", "Elephant", "Wolf", "Eagle", "Shark"]
animal = random.choice(animals)
print(f"🎬 Creating short for {animal}")

# 🖼️ تحميل الصور
PEXELS_API = os.environ.get("PEXELS_API_KEY")
headers = {"Authorization": PEXELS_API}
res = requests.get(f"https://api.pexels.com/v1/search?query={animal}&per_page=5", headers=headers).json()
images = [photo["src"]["medium"] for photo in res["photos"]]

os.makedirs("frames", exist_ok=True)
for idx, url in enumerate(images):
    img_data = requests.get(url).content
    with open(f"frames/frame{idx}.jpg", "wb") as f:
        f.write(img_data)

# 🎵 موسيقى خلفية
music_url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Scott_Holmes_Music/Happy_Music/Scott_Holmes_Music_-_Happy_Whistle.mp3"
music_path = "music.mp3"
if not os.path.exists(music_path):
    open(music_path, "wb").write(requests.get(music_url).content)

clip = ImageSequenceClip(["frames/" + f for f in os.listdir("frames")], fps=1)
audio = AudioFileClip(music_path).volumex(0.3)

# 📝 كتابة اسم الحيوان كعنوان في الفيديو
text = TextClip(f"{animal} in Nature 🐾", fontsize=40, color='white', bg_color='black', size=(720, 120))
text = text.set_duration(audio.duration).set_position(("center", "bottom"))
final_video = CompositeVideoClip([clip.set_audio(audio), text])
file_name = f"{animal.lower()}_short.mp4"
final_video.write_videofile(file_name, fps=24)

# 📈 تحسين SEO
title = f"{animal} In Action 🐾 | AI Wildlife Short #Shorts"
description = f"Relax and enjoy this AI-generated short about the {animal}. Music only 🎵\n\n#Shorts #Wildlife #Animals #AI"
tags = [animal.lower(), "shorts", "wildlife", "AI", "nature", "animals"]

# ⏰ أفضل توقيت نشر
current_hour = datetime.datetime.utcnow().hour
if current_hour < 12:
    schedule_time = "Evening (USA)"
else:
    schedule_time = "Morning (Europe)"
print(f"🕓 Scheduled for {schedule_time}")

print("🚀 Uploading short...")
upload_video(file_name, title, description, tags)
