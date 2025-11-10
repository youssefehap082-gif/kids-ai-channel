import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import random
from youtube import list_recent_videos, get_video_stats_bulk
from utils import get_trending_animals, get_thumbnail_path, generate_animal_description, generate_hashtags


def analyze_video_performance(videos):
    """
    تحليل أداء الفيديوهات السابقة لتحديد الأنواع الأفضل أداءً.
    """
    stats = get_video_stats_bulk([v["id"] for v in videos])
    performance = {}

    for video, stat in zip(videos, stats):
        title = video["title"]
        views = int(stat.get("viewCount", 0))
        likes = int(stat.get("likeCount", 0))
        comments = int(stat.get("commentCount", 0))

        score = (views * 0.6) + (likes * 0.3) + (comments * 0.1)
        animal = extract_animal_from_title(title)

        if animal:
            if animal not in performance:
                performance[animal] = []
            performance[animal].append(score)

    avg_scores = {a: sum(s) / len(s) for a, s in performance.items()}
    return sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)


def extract_animal_from_title(title):
    """
    استخراج اسم الحيوان من العنوان لو موجود.
    """
    title = title.lower()
    animals = [
        "lion", "tiger", "bear", "eagle", "shark", "wolf", "elephant",
        "cheetah", "giraffe", "leopard", "panda", "zebra", "monkey",
        "rhino", "hippo", "kangaroo", "fox", "crocodile", "gorilla",
        "dolphin", "snake", "owl", "cat", "dog", "whale"
    ]
    for animal in animals:
        if animal in title:
            return animal
    return None


def optimize_next_videos():
    """
    تشغيل الذكاء الاصطناعي لتحليل الفيديوهات وتحديد حيوانات اليوم التالي.
    """
    print("🧠 Starting AI Optimizer...")
    try:
        recent_videos = list_recent_videos(limit=20)
    except Exception as e:
        print("⚠️ Failed to get recent videos:", e)
        return

    if not recent_videos:
        print("⚠️ No videos found to analyze.")
        trending_animals = get_trending_animals(5)
        save_optimized_animals(trending_animals)
        return

    ranking = analyze_video_performance(recent_videos)
    top_animals = [r[0] for r in ranking[:5]] if ranking else []
    print("🔥 Top trending animals (from channel):", top_animals)

    trending_animals = get_trending_animals(5)
    print("🌍 External trending animals (from API):", trending_animals)

    # دمج القائمتين بدون تكرار
    merged_list = list(set(top_animals + trending_animals))
    print("✅ Final optimized animal list:", merged_list)

    save_optimized_animals(merged_list)


def save_optimized_animals(animal_list):
    """
    حفظ قائمة الحيوانات النهائية في ملف JSON لاستخدامها لاحقًا.
    """
    data = {
        "optimized_animals": animal_list,
        "count": len(animal_list)
    }

    try:
        with open("optimized_animals.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 Saved optimized data to optimized_animals.json")

        # إنشاء وصف وهاشتاج لكل حيوان لتستخدمها الفيديوهات القادمة
        details = []
        for animal in animal_list:
            desc = generate_animal_description(animal)
            tags = generate_hashtags(animal)
            thumb = get_thumbnail_path(animal)
            details.append({
                "animal": animal,
                "description": desc,
                "hashtags": tags,
                "thumbnail": thumb
            })

        with open("animal_details.json", "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        print("📁 Created animal_details.json for next videos.")
    except Exception as e:
        print("⚠️ Failed to save optimized animals:", e)


if __name__ == "__main__":
    optimize_next_videos()
