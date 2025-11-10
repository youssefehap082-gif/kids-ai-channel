import os
import re
import tempfile
import json
import requests
import random


def get_trending_animals(limit=5):
    """
    دالة ترجع قائمة بحيوانات ترند بناءً على مصادر مختلفة (API أو قائمة جاهزة).
    """
    print("🌍 Fetching trending animals...")
    try:
        # ممكن تستخدم API حقيقية هنا لو عندك مفتاح من موقع بيقدم ترندات الحيوانات
        trending = [
            "lion", "tiger", "panda", "wolf", "shark", "elephant",
            "eagle", "cheetah", "zebra", "fox", "bear", "monkey",
            "crocodile", "giraffe", "leopard", "rhino", "dolphin",
            "octopus", "gorilla", "whale"
        ]
        random.shuffle(trending)
        return trending[:limit]
    except Exception as e:
        print("⚠️ Error fetching trending animals:", e)
        # fallback list
        return ["lion", "tiger", "bear", "eagle", "shark"][:limit]


def get_thumbnail_path(animal: str):
    """
    ينشئ مسار آمن لصورة مصغرة للحيوان.
    """
    safe_name = re.sub(r'\W+', '_', animal.lower())
    path = os.path.join(tempfile.gettempdir(), f"thumb_{safe_name}.png")
    return path


def save_json(data, filename="data.json"):
    """
    حفظ بيانات في ملف JSON مؤقت.
    """
    try:
        path = os.path.join(tempfile.gettempdir(), filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved JSON file: {path}")
        return path
    except Exception as e:
        print("⚠️ Failed to save JSON:", e)
        return None


def read_json(filename="data.json"):
    """
    قراءة ملف JSON محلي.
    """
    try:
        path = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print("⚠️ Failed to read JSON:", e)
        return {}


def generate_animal_description(animal):
    """
    إنشاء وصف نصي بسيط عن الحيوان بناءً على اسمه.
    """
    facts = [
        f"The {animal} is one of the most fascinating creatures on Earth.",
        f"Did you know? The {animal} has unique features that make it special.",
        f"Learn 10 amazing facts about the {animal} today!",
        f"The {animal} plays an important role in nature and ecosystems.",
        f"Watch and discover more about the incredible {animal}."
    ]
    description = random.choice(facts)
    print(f"🦁 Generated description for {animal}: {description}")
    return description


def generate_hashtags(animal):
    """
    إنشاء مجموعة هاشتاجات ذكية لكل حيوان.
    """
    hashtags = [
        f"#{animal}",
        f"#{animal}Facts",
        "#Wildlife",
        "#Nature",
        "#Animals",
        "#Discover",
        "#Explore",
        "#WildFactsHub"
    ]
    return list(set(hashtags))


def download_image_from_api(animal):
    """
    تنزيل صورة أو فيديو من Pixabay أو Pexels كصورة مصغرة مؤقتة.
    """
    try:
        api_key = os.getenv("PEXELS_API_KEY") or os.getenv("PIXABAY_API_KEY")
        if not api_key:
            print("⚠️ No API key for Pexels/Pixabay found.")
            return None

        query = f"{animal} animal"
        url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&per_page=3"
        r = requests.get(url)
        data = r.json()

        if "hits" in data and len(data["hits"]) > 0:
            image_url = data["hits"][0]["largeImageURL"]
            response = requests.get(image_url)
            path = get_thumbnail_path(animal)
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"✅ Downloaded thumbnail for {animal}")
            return path
        else:
            print(f"⚠️ No image found for {animal}")
            return None
    except Exception as e:
        print("⚠️ Error downloading image:", e)
        return None
