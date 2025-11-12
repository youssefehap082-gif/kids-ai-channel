import os
from pexelspy import Pexels

# 1. حط مفتاح Pexels API بتاعك هنا
PEXELS_API_KEY = "YOUR_PEXELS_API_KEY"

# 2. الكلمة اللي عايز تبحث عنها
SEARCH_QUERY = "nature sunset"

def get_free_video():
    if PEXELS_API_KEY == "YOUR_PEXELS_API_KEY":
        print("خطأ: لازم تحط Pexels API Key بتاعك الأول!")
        return

    try:
        pexel = Pexels(PEXELS_API_KEY)
        search_results = pexel.search_videos(
            query=SEARCH_QUERY,
            orientation="portrait",  # أو 'landscape' للفيديو العادي
            size="medium",
            per_page=1
        )
        
        if not search_results.videos:
            print(f"للأسف، مفيش فيديوهات لكلمة '{SEARCH_QUERY}'")
            return

        # 3. الحصول على رابط أول فيديو
        video = search_results.videos[0]
        video_link = video.video_files[0].link # بنختار أول جودة متاحة

        print(f"تم العثور على فيديو: {video.url}")
        print(f"رابط التحميل المباشر: {video_link}")
        
        # هنا ممكن تضيف كود لتحميل الفيديو باستخدام مكتبة requests
        # بس الأسهل تبدأ بالرابط ده

    except Exception as e:
        print(f"حصلت مشكلة: {e}")

if __name__ == "__main__":
    get_free_video()
