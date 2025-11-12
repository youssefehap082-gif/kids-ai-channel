# tools/generator.py
import os, json, time, tempfile, requests
from pathlib import Path
from seo import make_title_description_tags
from tts_eleven import synthesize_eleven
from media_collector import fetch_images_and_videos
from composer import compose_long_video, compose_short_video
from uploader import upload_video_to_youtube

WORKDIR = Path("workspace")
ASSETS = Path("workspace/assets")
os.makedirs(ASSETS, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_facts_for_animal(animal):
    # Use OpenAI to generate 10 interesting facts in plain English.
    # This function expects OPENAI_API_KEY present.
    import openai
    openai.api_key = OPENAI_API_KEY
    prompt = f"Provide 10 concise, engaging facts (bullet points) about the animal '{animal}'. Use simple clear English suitable for a wide audience. Each fact must be 1 sentence. Do NOT include numbering in the output — return as JSON array of strings."
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=400
    )
    content = resp.choices[0].message.content.strip()
    # try to parse JSON, fallback: split lines
    try:
        facts = json.loads(content)
        if isinstance(facts, list):
            return facts[:10]
    except Exception:
        # fallback: split by lines and take first 10
        lines = [l.strip("-• \t") for l in content.splitlines() if l.strip()]
        return lines[:10]
    return []

def generate_long_video(animal, test_run=False):
    facts = generate_facts_for_animal(animal)
    if not facts:
        facts = [f"Interesting fact about {animal}."]*10

    # Prepare voice selection: alternate male/female using a simple toggle file
    toggle_file = WORKDIR / "voice_toggle.json"
    if toggle_file.exists():
        t = json.loads(toggle_file.read_text())
        last = t.get("last","female")
    else:
        last = "female"
    voice = "male" if last=="female" else "female"
    toggle_file.write_text(json.dumps({"last": voice}), encoding='utf-8')

    # Build script text (10 facts + CTA)
    lines = []
    for i,f in enumerate(facts,1):
        lines.append(f"{i}. {f}")
    lines.append("") 
    lines.append("Don't forget to subscribe and hit the bell for more!")

    script_text = "\n".join(lines)

    # synthesize voice via ElevenLabs
    audio_path = ASSETS / f"{animal}_long_audio.mp3"
    synthesize_eleven(script_text, voice=voice, out_path=str(audio_path))

    # fetch media (images/videos)
    media_folder = ASSETS / f"{animal}_media"
    media_folder.mkdir(parents=True, exist_ok=True)
    fetch_images_and_videos(animal, out_folder=str(media_folder), needed_images=12, needed_videos=3)

    # compose with moviepy
    title, description, tags = make_title_description_tags(animal, facts)
    video_path = WORKDIR / f"{animal}long{int(time.time())}.mp4"
    compose_long_video(str(media_folder), str(audio_path), str(video_path), facts, cta_text="Don't forget to subscribe and hit the bell for more!")

    # upload
    res = upload_video_to_youtube(video_path=str(video_path), title=title, description=description, tags=tags, privacyStatus="public" if not test_run else "unlisted")
    # log upload result
    LOG = WORKDIR / "upload_log.json"
    logs = []
    if LOG.exists():
        logs = json.loads(LOG.read_text())
    logs.append({"animal":animal, "video": str(video_path), "youtube": res, "timestamp": time.time()})
    LOG.write_text(json.dumps(logs, indent=2))
    return {"local": str(video_path), "youtube": res}

def generate_short_video(animal):
    # Shorts: no voice, music only. 15-30 sec.
    facts = []  # not used; just images + music
    media_folder = ASSETS / f"{animal}_media"
    media_folder.mkdir(parents=True, exist_ok=True)
    fetch_images_and_videos(animal, out_folder=str(media_folder), needed_images=6, needed_videos=1)
    short_path = WORKDIR / f"{animal}short{int(time.time())}.mp4"
    compose_short_video(str(media_folder), out_path=str(short_path))
    # upload as 'shorts' with short title
    title = f"{animal.replace('_',' ').title()} Facts (Short)"
    description = f"Short video about {animal}. Music only."
    tags = [f"#{animal.replace('_','')}", "#animals", "#shorts"]
    res = upload_video_to_youtube(video_path=str(short_path), title=title, description=description, tags=tags, privacyStatus="public")
    return {"local": short_path, "youtube": res}
