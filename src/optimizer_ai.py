import json
import os
from utils import get_trending_animals, get_video_stats_bulk

print("🔍 Running AI optimizer...")

def main():
    trending = get_trending_animals()
    print("📈 Trending animals updated:", trending)
    
    # حفظ التريند في ملف
    os.makedirs("data", exist_ok=True)
    with open("data/trending_animals.json", "w", encoding="utf-8") as f:
        json.dump(trending, f, ensure_ascii=False, indent=2)
    print("✅ Saved trending animals data successfully.")

if __name__ == "__main__":
    main()
