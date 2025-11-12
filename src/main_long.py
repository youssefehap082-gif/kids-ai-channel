import os
import random
import requests
from moviepy.editor import ImageSequenceClip, AudioFileClip, TextClip, CompositeVideoClip
from gtts import gTTS
from youtube import upload_video
import datetime

# 🦁 بيانات الحيوانات والمعلومات
animals = {
    "Lion": "The lion is the king of the jungle, known for its strength and pride.",
    "Elephant": "Elephants are the largest land animals with incredible intelligence and memory.",
    "Tiger": "Tigers are powerful hunters and the largest members of the cat family.",
    "Panda": "Pandas are calm, bamboo-loving bears known for their cuteness.",
    "Wolf": "Wolves are loyal, smart, and live in social packs.",
    "Eagle": "Eagles are known for their powerful flight and exceptional vision.",
    "Shark": "Sharks have existed for over 400 million years, even before dinosaurs!"
}

animal, fact = random.choice(list(animals.items()))
print(f"🎬 Generating long video for {animal}")

# 🎤 تبديل الصوت بين ذكر وأنثى
voice_gender = random.choice(["male", "female"])
tts = gTTS(text=f"Here are some amazing facts about the {animal}. {fact}", lang="en", slow=False)
tts.save("voice.mp3")

# 🖼️ تحميل صور من Pexels
PEXELS_API = os.environ.get("PEXELS_API_KEY")
headers = {"Authorization": PEXELS_API}
res = requests.get(f"https://api.pexels.com/v1/search?query={animal}&per_page=8", headers=headers).json()
images = [photo["src"]["medium"] for photo in res["photos"]]

os.makedirs("frames", exist_ok=True)
for idx, url in enumerate(images):
    img_data = requests.get(url).content
    with open(f"frames/frame{idx}.jpg", "wb") as f:
        f.write(img_data)

# 🎥 إنشاء الفيديو
clip = ImageSequenceClip(["frames/" + f for f in os.listdir("frames")], fps=1)
audio = AudioFileClip("voice.mp3")

# 📝 إضافة الترجمة النصية
subtitle = TextClip(f"{fact}", fontsize=32, color='white', bg_color='black', size=(720, 100))
subtitle = subtitle.set_duration(audio.duration).set_position(("center", "bottom"))
final_clip = CompositeVideoClip([clip.set_audio(audio), subtitle])
file_name = f"{animal.lower()}_documentary.mp4"
final_clip.write_videofile(file_name, fps=24)

# 🧠 تحسين الـ SEO
title = f"Amazing Facts About The {animal} 🐾 | AI Wildlife Documentary"
description = f"Discover amazing facts about the {animal}! AI-generated documentary with narration and subtitles.\n\n#AI #Wildlife #Animals #Nature #Facts"
tags = [animal.lower(), "wildlife", "AI", "documentary", "animals", "facts"]

# ⏰ تحديد وقت النشر (أفضل مواعيد أمريكا وأوروبا)
current_hour = datetime.datetime.utcnow().hour
if current_hour < 12:
    schedule_time = "Evening (USA)"
else:
    schedule_time = "Morning (Europe)"
print(f"🕓 Scheduled for {schedule_time}")

print("🚀 Uploading...")
upload_video(file_name, title, description, tags)
