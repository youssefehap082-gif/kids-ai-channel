import json, random, os
from pexels import get_images_for_animal
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip

def get_copyright_music(duration=30):
    # موسيقى مجانية محلية أو روابط من pixabay أو pexels
    return "assets/music/free_music.mp3"

with open("animals/animals_list.json") as f:
    animals = json.load(f)

def pick_animals(n=5):
    return random.sample(animals, n)

def generate_short(animal):
    images = get_images_for_animal(animal["name"], count=5)
    music_path = get_copyright_music(duration=30)
    clip = ImageSequenceClip(images, fps=2)
    music = AudioFileClip(music_path)
    short_clip = clip.set_audio(music)
    out_path = f"outputs/short/{animal['name']}.mp4"
    short_clip.write_videofile(out_path, fps=24)
    return out_path

def main():
    animals_today = pick_animals(5)
    for animal in animals_today:
        short_path = generate_short(animal)
        print(f"Short Generated: {short_path}")

if __name__ == "__main__":
    main()
