import os
from youtube import upload_video
import random
import cv2
import numpy as np

# 🔧 إعداد فيديو قصير تلقائي
video_name = f"short_{random.randint(1000,9999)}.mp4"

print("🎬 Generating AI Short video...")
width, height = 720, 1280
out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), 24, (width, height))
for i in range(120):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, f"AI Short #{i}", (120, 640), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
    out.write(frame)
out.release()

# 🎥 معلومات الفيديو
title = f"🤖 Funny AI Short #{random.randint(1,9999)}"
description = "Daily AI Shorts generated automatically 🤖🔥"
tags = ["AI", "funny", "shorts", "automation"]

print("🚀 Uploading to YouTube...")
video_id = upload_video(video_name, title, description, tags)

if video_id:
    print(f"✅ Uploaded successfully: https://youtu.be/{video_id}")
else:
    print("❌ Upload failed!")
    exit(1)
