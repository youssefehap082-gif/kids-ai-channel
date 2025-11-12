import os
from pixabay import Pixabay

# 1. حط مفتاح Pixabay API بتاعك هنا
PIXABAY_API_KEY = "YOUR_PIXABAY_API_KEY"

# 2. الكلمات اللي عايز تبحث عنها
VIDEO_QUERY = "city traffic"
MUSIC_QUERY = "sad piano"

def get_free_media():
    if PIXABAY_API_KEY == "YOUR_PIXABAY_API_KEY":
        print("خطأ: لازم تحط Pixabay API Key بتاعك الأول!")
        return
        
    try:
        pix = Pixabay(PIXABAY_API_KEY)
        
        # 3. البحث عن فيديو
        video_results = pix.search(
            q=VIDEO_QUERY,
            media_type="video",
            video_type="animation", # أو 'film' أو 'all'
            per_page=3
        )
        
        if video_results['hits']:
            first_video = video_results['hits'][0]
            print(f"\n--- نتيجة الفيديو ---")
            print(f"رابط صفحة الفيديو: {first_video['pageURL']}")
            print(f"رابط التحميل (جودة متوسطة): {first_video['videos']['medium']['url']}")
        else:
            print(f"\nمفيش فيديوهات لكلمة '{VIDEO_QUERY}'")

        # 4. البحث عن موسيقى
        music_results = pix.search(
            q=MUSIC_QUERY,
            media_type="music", # هنا بنحدد إننا عايزين موسيقى
            per_page=3
        )
        
        if music_results['hits']:
            first_track = music_results['hits'][0]
            print(f"\n--- نتيجة الموسيقى ---")
            print(f"رابط صفحة المقطع: {first_track['pageURL']}")
            print(f"رابط التحميل المباشر: {first_track['audioFullURL']}") # رابط التحميل
        else:
            print(f"\nمفيش موسيقى لكلمة '{MUSIC_QUERY}'")
            
    except Exception as e:
        print(f"حصلت مشكلة: {e}")

if __name__ == "__main__":
    get_free_media()
