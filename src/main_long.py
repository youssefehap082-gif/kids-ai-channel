import os
from youtube import upload_video
import random
import cv2
import numpy as np

video_name = f"long_{random.randint(1000,9999)}.mp4"

print("🎬 Generating Long AI Video...")
width, height = 1280, 720
out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), 24, (width, height))
for i in range(600):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, f"Long AI Video Frame {i}", (300, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3)
    out.write(frame)
out.release()

# 📜 معلومات الفيديو
title = f"🎬 AI Long Video #{random.randint(1,9999)}"
description = "Daily AI Long Video generated automatically 🚀"
tags = ["AI", "long video", "automation"]

print("🚀 Uploading to YouTube...")
video_id = upload_video(video_name, title, description, tags)

if video_id:
    print(f"✅ Uploaded successfully: https://youtu.be/{video_id}")
else:
    print("❌ Upload failed!")
    exit(1)
