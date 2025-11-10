import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import random
from youtube import list_recent_videos, get_video_stats_bulk
from utils import get_trending_animals
from seo import generate_keywords
from subtitles import translate_text


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
        "rhino", "hippo", "kangaroo", "fox", "crocodile", "gorilla"
    ]
    for animal in animals:
        if animal in title:
            return animal
    return None


def optimize_next_videos():
    print("🧠 Starting AI Optimizer...")
    recent_videos = list_recent_videos(limit=50)
    if not recent_videos:
        print("⚠️ No videos found to analyze.")
        return

    ranking = analyze_video_performance(recent_videos)
    top_animals = [r[0] for r in ranking[:5]]  # أفضل 5 حيوانات أداءً
    print("🔥 Top trending animals:", top_animals)

    trending_animals = get_trending_animals(5)
    print("🌍 External trending animals:", trending_animals)

    merged_list = list(set(top_animals + trending_animals))
    print("✅ Final optimized animal list:", merged_list)

    data = {"optimized_animals": merged_list}
    with open("optimized_animals.json", "w") as f:
        json.dump(data, f)

    print("💾 Saved optimized data to optimized_animals.json")


if __name__ == "__main__":
    optimize_next_videos()
