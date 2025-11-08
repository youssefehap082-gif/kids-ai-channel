import os, tempfile, random
from pathlib import Path
from animals import load_animals_pool
from utils import pick_unique_animals
from media_sources import pick_video_urls
from compose import download_files, compose_short, pick_bg_music
from seo import shorts_title_for, hashtags_for, tags_for

ROOT = Path(__file__).resolve().parents[1]
POOL_CSV = ROOT / "data" / "animals_pool.csv"

def main():
    animals = load_animals_pool(POOL_CSV)
    chosen6 = pick_unique_animals(animals, n=6)

    from youtube import upload_video

    for idx, animal in enumerate(chosen6):
        print(f"🎥 Creating short for {animal} (music only)")
        urls = pick_video_urls(animal, need=8, prefer_vertical=True)
        paths = download_files(urls, Path(tempfile.mkdtemp()))

        # موسيقى من المجلد أو fallback
        music = pick_bg_music(ROOT / "assets/music")
        if not music:
            import requests
            r = requests.get("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
            tmp = Path(tempfile.mkdtemp()) / "music.mp3"
            tmp.write_bytes(r.content)
            music = tmp

        final = compose_short(paths, music, target_duration=58)

        title = shorts_title_for(animal)
        desc = f"Amazing animal moments about the {animal}! 🎶\n{hashtags_for(animal, shorts=True)}"
        tags = tags_for(animal) + ["shorts", "music", "animals"]

        upload_video(str(final), title, desc, tags, privacy="public", schedule_time_rfc3339=None)

if __name__ == "__main__":
    main()
