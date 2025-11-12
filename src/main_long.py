import os, random, cv2, numpy as np
from youtube import upload_video

# 🧠 توليد محتوى الفيديو
animals = ["Lion", "Panda", "Elephant", "Tiger", "Eagle", "Shark", "Dolphin", "Crocodile"]
animal = random.choice(animals)

file_name = f"long_{animal.lower()}_{random.randint(1000,9999)}.mp4"

print(f"🎬 Generating video about {animal}...")
width, height = 1280, 720
out = cv2.VideoWriter(file_name, cv2.VideoWriter_fourcc(*'mp4v'), 24, (width, height))

for i in range(400):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, f"{animal} Facts #{i}", (200, 360),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    out.write(frame)
out.release()

# 🎯 تحسين العنوان والوصف و الـ SEO
title = f"10 Amazing Facts About The {animal} You Didn’t Know 🐾"
description = (
    f"Discover mind-blowing facts about the {animal}! "
    "From wild nature secrets to unknown behaviors. "
    "Subscribe for more daily wildlife videos 🐾\n\n"
    "#wildlife #animals #nature #facts #documentary #AI"
)
tags = [animal.lower(), "animal facts", "wildlife", "nature", "AI video", "facts", "documentary"]

print("🚀 Uploading video to YouTube...")
video_id = upload_video(file_name, title, description, tags)

if video_id:
    print(f"✅ Uploaded: https://youtu.be/{video_id}")
else:
    print("❌ Upload failed!")
