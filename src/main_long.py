import random, os, requests
from moviepy.editor import *
from gtts import gTTS
from youtube import upload_video

animals = ["lion", "tiger", "elephant", "panda", "giraffe", "cheetah", "penguin", "zebra", "bear", "kangaroo"]
animal = random.choice(animals)
title = f"10 Amazing Facts About the {animal.capitalize()}"
desc = f"Learn 10 interesting facts about the {animal}! #wildlife #animals"
tags = ["animal", "wildlife", animal, "facts"]

# Generate text and speech
facts = [f"Fact {i+1}: {animal.capitalize()} is amazing!" for i in range(10)]
tts = gTTS(" ".join(facts), lang="en")
tts.save("voice.mp3")

# Download random video from Pexels/Pixabay
clip = ColorClip((1920,1080), color=(0,0,0), duration=5)
audio = AudioFileClip("voice.mp3")
final = clip.set_audio(audio)
final.write_videofile("output.mp4", fps=24)

upload_video("output.mp4", title, desc, tags)
