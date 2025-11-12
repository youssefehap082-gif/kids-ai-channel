import os, random, cv2, numpy as np
from youtube import upload_video

animals = ["Owl", "Koala", "Penguin", "Giraffe", "Monkey", "Snake", "Wolf"]
animal = random.choice(animals)

file_name = f"short_{animal.lower()}_{random.randint(1000,9999)}.mp4"

print(f"🎬 Creating AI Short about {animal}...")
width, height = 720, 1280
out = cv2.VideoWriter(file_name, cv2.VideoWriter_fourcc(*'mp4v'), 24, (width, height))

for i in range(150):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, f"{animal} Short #{i}", (180, 640),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    out.write(frame)
out.release()

title = f"{animal} In Action 🐾 #Shorts"
description = f"Watch this amazing {animal} in action! Subscribe for more daily AI animal shorts 🐾 #shorts #wildlife"
tags = [animal.lower(), "wildlife", "AI", "animals", "shorts", "nature", "funny"]

print("🚀 Uploading short video to YouTube...")
video_id = upload_video(file_name, title, description, tags)

if video_id:
    print(f"✅ Uploaded Short: https://youtu.be/{video_id}")
else:
    print("❌ Upload failed!")
