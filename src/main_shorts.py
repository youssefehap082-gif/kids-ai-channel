import random
from moviepy.editor import *
from youtube import upload_video

animals = ["lion", "eagle", "turtle", "fish", "frog", "panda"]
animal = random.choice(animals)
title = f"{animal.capitalize()} in Nature 🐾"
desc = f"Beautiful view of {animal}s in the wild. #Shorts #Nature #Animals"
tags = ["Shorts", "Animals", animal]

clip = ColorClip((1080,1920), color=(0,0,0), duration=10)
clip.write_videofile("short.mp4", fps=30)
upload_video("short.mp4", title, desc, tags)
