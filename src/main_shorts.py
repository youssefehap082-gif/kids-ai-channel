import os, tempfile, requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from animals import load_animals_pool
from utils import pick_unique_animals
from media_sources import pick_video_urls
from tts import synthesize
from compose import download_files, compose_short
from seo import shorts_title_for, hashtags_for, tags_for

ROOT = Path(__file__).resolve().parents[1]
POOL_CSV = ROOT / "data" / "animals_pool.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
OPENAI_MODEL = os.getenv("OPENAI_MODEL","gpt-4o-mini")

def one_snack_fact(animal: str) -> str:
    prompt = f"Give ONE surprising, accurate, kid-friendly fact about the {animal} in <= 18 words. Plain sentence."
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers={"Authorization": f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},
                      json={"model": OPENAI_MODEL, "messages":[{"role":"user","content":prompt}], "temperature":0.5})
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip().replace("\n"," ")

def schedule_6_shorts_today() -> list:
    now = datetime.now(timezone.utc)
    date = now.date()
    est_hours = [9,11,13,15,17,20]
    slots=[]
    for h in est_hours:
        dt_utc = datetime(date.year,date.month,date.day,h+5,0,tzinfo=timezone.utc)
        if dt_utc < now + timedelta(minutes=20):
            dt_utc += timedelta(days=1)
        slots.append(dt_utc.isoformat())
    return slots

def main():
    animals = load_animals_pool(POOL_CSV)
    chosen6 = pick_unique_animals(animals, n=6)
    slots = schedule_6_shorts_today()

    from youtube import upload_video

    for idx, animal in enumerate(chosen6):
        fact = one_snack_fact(animal)
        tts_path = Path(tempfile.mkdtemp())/"short_narration.mp3"
        synthesize(fact, tts_path, idx=idx)

        urls = pick_video_urls(animal, need=6, prefer_vertical=True)
        paths = download_files(urls, Path(tempfile.mkdtemp()))
        final = compose_short(paths, tts_path, target_duration=58)

        title = shorts_title_for(animal)
        desc = fact + "\n" + hashtags_for(animal, shorts=True)
        tags = tags_for(animal) + ["shorts", "vertical video"]

        upload_video(final, title, desc, tags, privacy="private", schedule_time_rfc3339=slots[idx])

if __name__ == "__main__":
    main()
