from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

# 1. أسماء ملفات الفيديو اللي عايز تجمعها
VIDEO_FILE_1 = "clip1.mp4"
VIDEO_FILE_2 = "clip2.mp4"

# 2. اسم الملف النهائي
FINAL_VIDEO_NAME = "final_video.mp4"

def combine_videos():
    # التأكد من وجود الملفات
    if not os.path.exists(VIDEO_FILE_1) or not os.path.exists(VIDEO_FILE_2):
        print(f"خطأ: لازم يكون عندك ملفين بالاسم {VIDEO_FILE_1} و {VIDEO_FILE_2} في نفس المجلد")
        return

    try:
        print("جاري تحميل المقاطع...")
        # 3. تحميل المقاطع
        clip1 = VideoFileClip(VIDEO_FILE_1)
        clip2 = VideoFileClip(VIDEO_FILE_2)
        
        print("جاري دمج المقاطع...")
        # 4. دمج المقاطع مع بعض بالترتيب
        final_clip = concatenate_videoclips([clip1, clip2])
        
        print(f"جاري حفظ الفيديو النهائي باسم {FINAL_VIDEO_NAME}...")
        # 5. حفظ الملف النهائي
        # (codec="libx264" و audio_codec="aac" لضمان التوافق)
        final_clip.write_videofile(FINAL_VIDEO_NAME, codec="libx264", audio_codec="aac")
        
        print("تم الانتهاء بنجاح!")

    except Exception as e:
        print(f"حصلت مشكلة أثناء المونتاج: {e}")

if __name__ == "__main__":
    combine_videos()
