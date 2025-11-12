# src/main_shorts.py
import os
import random
import time
from pathlib import Path
import requests
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip, TextClip

FRAMES_FOLDER = "temp_frames_shorts"
OUT_FOLDER = "generated_shorts"
Path(FRAMES_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUT_FOLDER).mkdir(parents=True, exist_ok=True)

ANIMALS = ["Lion","Tiger","Panda","Elephant","Wolf","Eagle","Giraffe","Dolphin"]

def fetch_images(animal, count=6):
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

def main():
    animal = random.choice(ANIMALS)
    print(f"🎬 Preparing short for {animal}")

    try:
        images = fetch_images(animal, count=6)
        image_paths = download_images(images, FRAMES_FOLDER)
    except Exception as e:
        print(f"⚠️ Pexels fetch failed: {e}. Using placeholders.")
        from PIL import Image
        image_paths = []
        for i in range(6):
            img = Image.new("RGB", (720,1280), color=(50+i*10,80+i*10,110+i*10))
            p = Path(FRAMES_FOLDER)/f"ph_{i}.jpg"
            img.save(p)
            image_paths.append(str(p))

    # background music (free)
    music_url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Scott_Holmes_Music/Happy_Music/Scott_Holmes_Music_-_Happy_Whistle.mp3"
    music_path = "music_shorts.mp3"
    if not Path(music_path).exists():
        r = requests.get(music_url, timeout=30)
        r.raise_for_status()
        Path(music_path).write_bytes(r.content)

    clip = ImageSequenceClip(image_paths, fps=1)
    audio = AudioFileClip(music_path).volumex(0.35)
    text = TextClip(f"{animal} 🐾", fontsize=50, color='white', bg_color='black', size=(clip.w, 120)).set_duration(audio.duration).set_position(("center","bottom"))
    final = CompositeVideoClip([clip.set_audio(audio), text]).set_duration(audio.duration)
    out_file = f"{OUT_FOLDER}/{animal.lower()}_{int(time.time())}.mp4"
    final.write_videofile(out_file, fps=24, verbose=False, logger=None)

    title = f"{animal} In Action 🐾 | AI Short #Shorts"
    description = f"Relax and enjoy this AI-generated short about {animal}. Music only.\n\n#shorts #wildlife #animals #AI"
    tags = [animal.lower(),"shorts","wildlife","AI","nature"]

    from youtube import upload_video
    upload_video(out_file, title, description, tags, language="en", privacy="public")

if __name__ == "__main__":
    main()
