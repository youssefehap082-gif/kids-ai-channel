# src/main_long.py
import os
import random
import datetime
import time
from pathlib import Path
import requests
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip, TextClip
from tts_utils import generate_tts
from helpers import generate_srt_from_text
from youtube import upload_video, upload_captions

# --- CONFIG ---
FRAMES_FOLDER = "temp_frames_long"
OUT_FOLDER = "generated"
Path(FRAMES_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUT_FOLDER).mkdir(parents=True, exist_ok=True)

ANIMALS = {
    "Lion": "The lion is the king of the jungle, powerful and majestic.",
    "Elephant": "Elephants are intelligent matriarchal animals with incredible memory.",
    "Dolphin": "Dolphins are social and intelligent marine mammals that use echolocation.",
    "Tiger": "Tigers are solitary hunters with unique stripes used for camouflage.",
    "Panda": "Pandas spend most of their day eating bamboo.",
    "Wolf": "Wolves are highly social animals that live and hunt in packs.",
    "Eagle": "Eagles have extraordinary vision and are excellent hunters.",
    "Shark": "Sharks have roamed the oceans for hundreds of millions of years."
}

def fetch_images(animal, count=8):
    PEXELS_API = os.getenv("PEXELS_API_KEY")
    headers = {"Authorization": PEXELS_API}
    url = f"https://api.pexels.com/v1/search?query={animal}&per_page={count}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    images = [p["src"]["large"] for p in data.get("photos", [])]
    return images

def download_images(urls, target_folder):
    Path(target_folder).mkdir(parents=True, exist_ok=True)
    paths = []
    for i, u in enumerate(urls):
        ext = ".jpg"
        p = Path(target_folder) / f"frame_{i}{ext}"
        r = requests.get(u, timeout=30)
        r.raise_for_status()
        p.write_bytes(r.content)
        paths.append(str(p))
    return paths

def make_video_from_images(image_paths, audio_path, out_path, add_cta_text=True, title_text=None):
    clip = ImageSequenceClip(image_paths, fps=1)
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    # subtitle area
    subtitle = TextClip(title_text or "", fontsize=40, color='white', bg_color='black', size=(clip.w, 100)).set_duration(duration).set_position(("center","bottom"))
    clips = [clip.set_audio(audio)]
    if title_text:
        clips.append(subtitle)
    final = CompositeVideoClip(clips).set_duration(duration)
    final.write_videofile(out_path, fps=24, verbose=False, logger=None)
    return out_path, duration

def main():
    animal = random.choice(list(ANIMALS.keys()))
    fact = ANIMALS[animal]
    print(f"🎬 Preparing long video about: {animal}")

    # alternate voice gender
    voice_gender = random.choice(["male","female"])
    tts_text = f"Hello! Here are a few amazing facts about the {animal}. {fact}. Don't forget to subscribe and hit the bell for more."
    voice_path = "voice_long.mp3"
    generate_tts(tts_text, out_path=voice_path, gender=voice_gender)

    # fetch images
    try:
        images = fetch_images(animal, count=8)
        image_paths = download_images(images, FRAMES_FOLDER)
    except Exception as e:
        print(f"⚠️ Pexels image fetch failed: {e}. Falling back to placeholders.")
        # create placeholder solid color images using moviepy fallback
        from PIL import Image
        image_paths = []
        for i in range(6):
            img = Image.new("RGB", (1280,720), color=(30+i*10, 60+i*10, 90+i*10))
            p = Path(FRAMES_FOLDER)/f"ph_{i}.jpg"
            img.save(p)
            image_paths.append(str(p))

    # build video
    out_file = f"{OUT_FOLDER}/{animal.lower()}_{int(time.time())}.mp4"
    title_text = f"Amazing Facts About The {animal}"
    out_file, duration = make_video_from_images(image_paths, voice_path, out_file, title_text=title_text)

    # generate SRT
    srt_text = generate_srt_from_text(tts_text, duration)
    srt_path = out_file.replace(".mp4", ".srt")
    Path(srt_path).write_text(srt_text, encoding="utf-8")

    # SEO
    title = f"Amazing Facts About The {animal} 🐾 | AI Documentary"
    description = f"Discover amazing facts about the {animal}. Narration, subtitles and HD visuals. Subscribe for daily wildlife videos!\n\n#wildlife #animals #AI #documentary"
    tags = [animal.lower(), "wildlife", "documentary", "AI", "facts", "nature"]

    # upload
    from youtube import upload_video, upload_captions
    video_id = upload_video(out_file, title, description, tags, language="en", privacy="public")
    if video_id:
        try:
            upload_captions(video_id, srt_path, language="en", name="English (auto)")
        except Exception as e:
            print(f"⚠️ Captions upload failed: {e}")

if __name__ == "__main__":
    main()
