# tools/generator.py
import os, time, json
from pathlib import Path
from text_generator import generate_animal_facts
from tts_free import synthesize_free_tts
from media_collector import fetch_images_and_videos_public
from composer import compose_long_video, compose_short_video
from seo import make_title_description_tags
from uploader import upload_video_to_youtube
from thumbnail import generate_thumbnail
from music_free import get_random_music
from translate import translate_text

WORKDIR = Path("workspace")
ASSETS = WORKDIR / "assets"
LOG = WORKDIR / "upload_log.json"

def log_upload(entry):
    data = []
    if LOG.exists():
        try:
            data = json.loads(LOG.read_text(encoding='utf-8'))
        except:
            data = []
    data.append(entry)
    LOG.write_text(json.dumps(data, indent=2), encoding='utf-8')

def generate_long_video(animal, test_run=True):
    print(f"[generator] Generating facts for {animal}")
    facts = generate_animal_facts(animal)
    facts = facts[:10]
    script = "\n".join([f"{i+1}. {f}" for i,f in enumerate(facts)])
    script += "\nDon't forget to subscribe and hit the bell for more!"

    # voice: alternate simple toggle
    toggle_file = WORKDIR / "voice_toggle.json"
    if toggle_file.exists():
        try:
            t = json.loads(toggle_file.read_text())
            last = t.get("last","female")
        except:
            last = "female"
    else:
        last = "female"
    voice = "male" if last=="female" else "female"
    toggle_file.write_text(json.dumps({"last": voice}))

    # synthesize with gTTS
    audio_path = ASSETS / f"{animal}audio{int(time.time())}.mp3"
    synthesize_free_tts(script, out_path=str(audio_path))

    # collect media (images/videos)
    media_folder = ASSETS / f"{animal}_media"
    media_folder.mkdir(parents=True, exist_ok=True)
    print("[generator] fetching media...")
    media_info = fetch_images_and_videos_public(animal, out_folder=str(media_folder), needed_images=12, needed_videos=2)

    # get background music (optional)
    music_path = ASSETS / f"{animal}music{int(time.time())}.mp3"
    mpath = get_random_music(out_path=str(music_path))
    if mpath is None and audio_path.exists():
        # proceed without music or use silent background
        mpath = None

    # compose video
    video_path = WORKDIR / f"{animal}long{int(time.time())}.mp4"
    compose_long_video(str(media_folder), str(audio_path), str(video_path), facts, background_music=mpath)

    # generate SEO
    title, description, tags = make_title_description_tags(animal, facts)

    # generate thumbnail (use first image if exists)
    thumb_path = WORKDIR / f"{animal}thumb{int(time.time())}.jpg"
    # find first image in media_folder
    first_image = None
    for ext in (".jpg",".png"):
        lst = list(Path(media_folder).glob(ext))
        if lst:
            first_image = lst[0]
            break
    if first_image:
        try:
            generate_thumbnail(animal.replace("_"," ").title(), image_url=str(first_image), out_path=str(thumb_path))
        except Exception as e:
            print("[generator] thumbnail generation failed:", e)

    # translate description (generate subtitles later if needed)
    translations = translate_text(description, languages=["es","fr","de","pt","it"])

    # upload
    privacy = "unlisted" if test_run else "public"
    print("[generator] uploading to YouTube...")
    try:
        res = upload_video_to_youtube(video_path=str(video_path), title=title, description=description, tags=tags, privacyStatus=privacy, thumbnail_path=str(thumb_path) if thumb_path.exists() else None)
    except Exception as e:
        res = {"error": str(e)}
    entry = {"animal":animal, "title":title, "video_local": str(video_path), "youtube_response": res, "time": time.time()}
    log_upload(entry)
    return entry

def generate_short_video(animal):
    media_folder = ASSETS / f"{animal}_media"
    media_folder.mkdir(parents=True, exist_ok=True)
    fetch_images_and_videos_public(animal, out_folder=str(media_folder), needed_images=6, needed_videos=1)
    short_path = WORKDIR / f"{animal}short{int(time.time())}.mp4"
    compose_short_video(str(media_folder), out_path=str(short_path))
    title = f"{animal.replace('_',' ').title()} Facts (Short)"
    description = f"Short video about {animal}."
    tags = [f"{animal.replace('_','')}", "animals", "shorts"]
    try:
        res = upload_video_to_youtube(video_path=str(short_path), title=title, description=description, tags=tags, privacyStatus="public")
    except Exception as e:
        res = {"error": str(e)}
    entry = {"animal":animal, "type":"short", "title":title, "video_local": str(short_path), "youtube_response": res, "time": time.time()}
    log_upload(entry)
    return entry
