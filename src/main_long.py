import os
from youtube import upload_video

# 🧠 مسار الفيديو (اختبار مؤقت)
test_video_path = "test_long.mp4"

# ✅ لو مفيش فيديو موجود، نعمل فيديو تجريبي بسيط مدته أطول
if not os.path.exists(test_video_path):
    import ffmpeg
    import numpy as np
    import cv2

    print("🎬 Generating long test video...")
    width, height = 1280, 720
    out = cv2.VideoWriter(test_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 24, (width, height))
    for i in range(500):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, f"Frame {i+1}", (400, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        out.write(frame)
    out.release()
    print("🎥 Long test video created!")

# 🧾 تفاصيل الفيديو
title = "🎬 Test Upload – AI Long Video Automation"
description = "This is a long test upload from GitHub Actions automation system."
tags = ["ai", "automation", "long video", "test"]

print("🚀 Uploading long video to YouTube...")
video_id = upload_video(test_video_path, title, description, tags)

if video_id:
    print(f"✅ Uploaded successfully! Video ID: {video_id}")
    os.environ["LAST_VIDEO_ID"] = video_id
else:
    print("❌ Upload failed, no video ID returned!")
    exit(1)
