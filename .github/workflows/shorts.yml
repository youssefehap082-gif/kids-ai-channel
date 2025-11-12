import os
from youtube import upload_video

# 🧠 هنا هتحط مسار الفيديو اللي بيتولد تلقائيًا من السكربت أو اختبار مؤقت
test_video_path = "test_short.mp4"

# ✅ لو مفيش فيديو جاهز، اعمل فيديو تجريبي بسيط علشان نختبر الرفع
if not os.path.exists(test_video_path):
    import ffmpeg
    import numpy as np
    import cv2

    print("🎬 Generating test video...")
    width, height = 720, 1280
    out = cv2.VideoWriter(test_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 24, (width, height))
    for i in range(100):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, f"Frame {i+1}", (200, 640), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        out.write(frame)
    out.release()
    print("🎥 Test video created!")

# 🧾 تفاصيل الفيديو
title = "🐾 Test Upload – AI Shorts Automation"
description = "This is a test upload from GitHub Actions automation."
tags = ["ai", "shorts", "automation", "test"]

print("🚀 Uploading to YouTube...")
video_id = upload_video(test_video_path, title, description, tags)

if video_id:
    print(f"✅ Uploaded successfully! Video ID: {video_id}")
    os.environ["LAST_VIDEO_ID"] = video_id
else:
    print("❌ Upload failed, no video ID returned!")
    exit(1)
