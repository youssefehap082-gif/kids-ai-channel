import os, tempfile, requests, time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from animals import load_animals_pool
from utils import pick_unique_animals, chunk_text
from media_sources import pick_video_urls
from tts import synthesize
from compose import download_files, make_voicebed, compose_video, pick_bg_music
from seo import title_for, description_for, tags_for, hashtags_for

ROOT = Path(__file__).resolve().parents[1]
POOL_CSV = ROOT / "data" / "animals_pool.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
OPENAI_MODEL = os.getenv("OPENAI_MODEL","gpt-4o-mini")
USE_BG_MUSIC = os.getenv("USE_BG_MUSIC","false").lower() == "true"

def gen_facts(animal: str) -> list:
    prompt = f"""
Generate exactly 10 concise, verifiable facts about the {animal} in English.
One sentence per fact (<= 20 words). Neutral educational tone. Numbered list.
"""
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers={"Authorization": f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},
                      json={"model": OPENAI_MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0.4})
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"]
    lines = [l.strip(" -") for l in txt.split("\n") if l.strip()]
    facts=[]
    for l in lines:
        l2 = l.split(".",1)[-1].strip() if l[0].isdigit() else l
        facts.append(l2)
        if len(facts)==10: break
    return facts

def narration_script(animal: str, facts: list) -> str:
    intro = f"Here are ten amazing facts about the {animal}."
    outro = ("Don’t forget to subscribe to our channel and turn on the notification bell!"
             "\nSee you in the next video.")
    bullets = [f"Fact {i+1}. {f}" for i,f in enumerate(facts)]
    return "\n".join([intro] + bullets + [outro])

def schedule_slots_us_today(n: int) -> list:
    now = datetime.now(timezone.utc)
    date = now.date()
    # أفضل 3 مواعيد EST للجمهور الأمريكي: 11 AM, 4 PM, 8 PM
    est_hours = [11, 16, 20]
    slots=[]
    for h in est_hours[:n]:
        hour_utc = (h + 5) % 24
        dt_utc = datetime(date.year,date.month,date.day,hour_utc,0,tzinfo=timezone.utc)
        if dt_utc < now + timedelta(minutes=30):
            dt_utc += timedelta(days=1)
        slots.append(dt_utc.isoformat())
    return slots

def main():
    animals = load_animals_pool(POOL_CSV)
    chosen = pick_unique_animals(animals, n=3)
    slots = schedule_slots_us_today(n=3)

    from youtube import upload_video

    for idx, animal in enumerate(chosen):
        print(f"🎬 Generating video for: {animal}")
        facts = gen_facts(animal)
        script = narration_script(animal, facts)

        parts = chunk_text([script], max_chars=3200)
        voice_paths=[]
        for i, part in enumerate(parts):
            vp = Path(tempfile.mkdtemp())/f"voice_{i}.mp3"
            synthesize(part, vp, idx=idx)
            voice_paths.append(vp)

        bg = pick_bg_music(ROOT/"assets/music") if USE_BG_MUSIC else None
        voicebed = make_voicebed(voice_paths, bg_music=bg, music_gain_db=-18)

        urls = pick_video_urls(animal, need=10, prefer_vertical=False)
        paths = download_files(urls, Path(tempfile.mkdtemp()))
        final = compose_video(paths, voicebed, min_duration=185)

        title = title_for(animal)
        desc = description_for(animal, facts) + "\n\n" + hashtags_for(animal)
        tags = tags_for(animal)

        upload_video(final, title, desc, tags, privacy="private", schedule_time_rfc3339=slots[idx])
        time.sleep(10)

if __name__ == "__main__":
    main()
