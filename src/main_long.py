import os
import random
import requests
from moviepy.editor import ImageSequenceClip, AudioFileClip
from gtts import gTTS
from youtube import upload_video

# 🦁 قائمة الحيوانات
animals = [
    ("Lion", "The lion is known as the king of the jungle. It lives in groups called prides and can roar so loud it’s heard from 8 kilometers away."),
    ("Elephant", "Elephants are the largest land animals on Earth. They have an incredible memory and communicate using low-frequency sounds."),
    ("Tiger", "Tigers are strong hunters that can swim very well. Each tiger has unique stripes, just like human fingerprints."),
    ("Panda", "Pandas spend up to 12 hours a day eating bamboo and are known for their calm and playful nature."),
    ("Eagle", "Eagles have extremely sharp vision and can spot prey from over 3 kilometers away."),
    ("Wolf", "Wolves are intelligent and social animals that live and hunt in packs."),
    ("Shark", "Sharks have existed for more than 400 million years, even before dinosaurs.")
]

animal, fact = random.choice(animals)
print(f"🎬 Creating documentary for {animal}")

# 🎤 توليد الصوت من النص
tts = gTTS(text=f"Here are some amazing facts about the {animal}. {fact}", lang="en")
tts.save("voice.mp3")

# 🖼️ تحميل صور من Pexels API
PEXELS_API = os.environ.get("PEXELS_API_KEY")
headers = {"Authorization": PEXELS_API}
res = requests.get(f"https://api.pexels.com/v1/search?query={animal}&per_page=10", headers=headers).json()
images = [photo["src"]["medium"] for photo in res["photos"]]

# تنزيل الصور مؤقتًا
os.makedirs("frames", exist_ok=True)
for idx, url in enumerate(images):
    img_data = requests.get(url).content
    with open(f"frames/frame{idx}.jpg", "wb") as f:
        f.write(img_data)

# 🎥 إنشاء الفيديو من الصور
clip = ImageSequenceClip(["frames/" + f for f in os.listdir("frames")], fps=1)
audio = AudioFileClip("voice.mp3")
final_video = clip.set_audio(audio)
file_name = f"{animal.lower()}_documentary.mp4"
final_video.write_videofile(file_name, fps=24)

# 🧠 توليد العنوان والوصف والـ SEO
title = f"Amazing Facts About The {animal} 🐾 | AI Documentary"
description = f"Discover fascinating facts about the {animal}! AI-generated video with voice narration. #wildlife #animals #AI #documentary"
tags = [animal.lower(), "wildlife", "documentary", "AI", "facts", "nature"]

print("🚀 Uploading...")
upload_video(file_name, title, description, tags)
