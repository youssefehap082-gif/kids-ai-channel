import os, random, requests, datetime, time
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip, TextClip
from youtube import upload_video

animals = ["Lion", "Tiger", "Panda", "Elephant", "Wolf", "Eagle", "Giraffe", "Dolphin"]
animal = random.choice(animals)
print(f"🎬 Generating short for {animal}")

PEXELS_API = os.getenv("PEXELS_API_KEY")
headers = {"Authorization": PEXELS_API}
res = requests.get(f"https://api.pexels.com/v1/search?query={animal}&per_page=6", headers=headers).json()
images = [photo["src"]["medium"] for photo in res["photos"]]

os.makedirs("frames", exist_ok=True)
for i, url in enumerate(images):
    img_data = requests.get(url).content
    with open(f"frames/frame{i}.jpg", "wb") as f:
        f.write(img_data)

music_url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Scott_Holmes_Music/Happy_Music/Scott_Holmes_Music_-_Happy_Whistle.mp3"
open("music.mp3", "wb").write(requests.get(music_url).content)
clip = ImageSequenceClip(["frames/" + f for f in os.listdir("frames")], fps=1)
audio = AudioFileClip("music.mp3").volumex(0.4)

text = TextClip(f"{animal} 🐾", fontsize=50, color='white', bg_color='black', size=(720, 120)).set_duration(audio.duration).set_position(("center", "bottom"))
final = CompositeVideoClip([clip.set_audio(audio), text])
file_name = f"{animal.lower()}_short.mp4"
final.write_videofile(file_name, fps=24)

title = f"{animal} In Action 🐾 #Shorts"
description = f"Relax and enjoy this AI short about {animal}! #Wildlife #AI #Animals"
tags = [animal.lower(), "AI", "shorts", "wildlife", "nature"]

upload_video(file_name, title, description, tags)
