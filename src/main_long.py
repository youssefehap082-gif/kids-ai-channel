import os, tempfile, requests, time
from pathlib import Path
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

SUBSCRIBE_LINE = "Don’t forget to subscribe to our channel and turn on the notification bell!"

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
    bullets = [f"Fact {i+1}. {f}" for i,f in enumerate(facts)]
    outro = SUBSCRIBE_LINE
    return "\n".join([intro] + bullets + [outro])

def main():
    animals = load_animals_pool(POOL_CSV)
    chosen = pick_unique_animals(animals, n=3)

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

        urls = pick_video_urls(animal, need=12, prefer_vertical=False)
        paths = download_files(urls, Path(tempfile.mkdtemp()))
        final = compose_video(paths, voicebed, min_duration=185)

        title = title_for(animal)
        desc = description_for(animal, facts) + "\n\n" + hashtags_for(animal)
        tags = tags_for(animal)

        # ينزل Public فورًا
        from pathlib import Path as _P
        upload_video(str(final), title, desc, tags, privacy="public", schedule_time_rfc3339=None)
        time.sleep(5)

if __name__ == "__main__":
    main()
