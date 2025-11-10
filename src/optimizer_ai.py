import os
import requests
import json
import random
import datetime
from googleapiclient.discovery import build

from dotenv import load_dotenv
from utils import get_video_stats, get_trending_animals

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_youtube_trending_animals():
    """
    بيجيب الحيوانات أو المواضيع اللي طالعة تريند من اليوتيوب
    """
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode="US",
            videoCategoryId="15",  # category: Pets & Animals
            maxResults=30
        )
        response = request.execute()

        trending = []
        for item in response.get("items", []):
            title = item["snippet"]["title"].lower()
            if any(animal in title for animal in [
                "cat", "dog", "lion", "tiger", "bear", "snake",
                "fish", "elephant", "bird", "wolf", "horse",
                "panda", "monkey", "fox", "shark", "dolphin"
            ]):
                trending.append(title)
        print(f"✅ YouTube trending animals found: {len(trending)}")
        return trending
    except Exception as e:
        print(f"⚠️ Error fetching YouTube trending: {e}")
        return []

def get_google_trends_animals():
    """
    بيجيب الحيوانات اللي تريند عالميًا من Google Trends
    """
    try:
        import pytrends
        from pytrends.request import TrendReq
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=["animals", "wildlife", "zoo", "exotic animals"])
        related = pytrend.related_queries()
        keywords = []
        for kw in related.values():
            if kw and "top" in kw:
                keywords += [row["query"] for _, row in kw["top"].iterrows() if any(x.isalpha() for x in row["query"])]
        print(f"✅ Google Trends found {len(keywords)} animal-related keywords.")
        return list(set(keywords))
    except Exception as e:
        print(f"⚠️ Google Trends error: {e}")
        return []

def get_reddit_trending_animals():
    """
    بيجيب الحيوانات اللي عليها تفاعل عالي من Reddit
    """
    try:
        headers = {'User-Agent': 'WildFactsBot/1.0'}
        res = requests.get("https://www.reddit.com/r/Animals/top.json?t=day&limit=25", headers=headers)
        posts = res.json().get("data", {}).get("children", [])
        titles = [p["data"]["title"] for p in posts]
        print(f"✅ Reddit trending posts fetched: {len(titles)}")
        return titles
    except Exception as e:
        print(f"⚠️ Reddit trending fetch error: {e}")
        return []

def optimize_channel():
    """
    بيجمع كل المصادر ويعمل منها تحليل ذكي يختار المواضيع الأفضل للفيديوهات القادمة
    """
    print("🤖 Running Smart Optimization...")
    youtube_trends = get_youtube_trending_animals()
    google_trends = get_google_trends_animals()
    reddit_trends = get_reddit_trending_animals()

    all_trends = list(set(youtube_trends + google_trends + reddit_trends))
    if not all_trends:
        print("⚠️ No trending data found, using fallback animal list.")
        all_trends = get_trending_animals()

    selected = random.sample(all_trends, min(10, len(all_trends)))
    print(f"🔥 Selected trending animals/topics: {selected}")

    # نحفظ النتائج علشان الـ main_long.py و main_shorts.py يستخدموها
    os.makedirs("data", exist_ok=True)
    with open("data/trending_animals.json", "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)
    print("✅ Optimization complete, results saved!")

if __name__ == "__main__":
    optimize_channel()
