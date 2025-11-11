import random

# مجموعة روابط افتراضية لفيديوهات الحيوانات (تقدر تطورها لاحقاً)
ANIMAL_VIDEO_URLS = {
    "cat": [
        "https://www.pexels.com/video/856001/",
        "https://www.pexels.com/video/45201/",
        "https://www.pexels.com/video/12345/"
    ],
    "dog": [
        "https://www.pexels.com/video/857004/",
        "https://www.pexels.com/video/98765/",
        "https://www.pexels.com/video/43210/"
    ],
    "lion": [
        "https://www.pexels.com/video/99887/",
        "https://www.pexels.com/video/22331/"
    ],
    "bird": [
        "https://www.pexels.com/video/77777/",
        "https://www.pexels.com/video/88888/"
    ]
}

def pick_video_urls(animal: str, count: int = 2):
    """
    ترجع قائمة روابط لفيديوهات خاصة بالحيوان المطلوب
    """
    if animal not in ANIMAL_VIDEO_URLS:
        # لو الحيوان مش في القائمة، نختار أي حاجة عشوائي
        all_urls = sum(ANIMAL_VIDEO_URLS.values(), [])
        return random.sample(all_urls, min(count, len(all_urls)))
    else:
        urls = ANIMAL_VIDEO_URLS[animal]
        return random.sample(urls, min(count, len(urls)))
