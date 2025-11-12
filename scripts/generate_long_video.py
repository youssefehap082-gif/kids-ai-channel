import json, random, os
from elevenlabs import generate_voice_over   # اضبط المكتبة حسب المتاح لديك
from openai import get_animal_facts
from pexels import get_images_for_animal
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip

def get_copyright_music(duration=120):
    # استخدم ملف محلي أو حمل من pixabay mp3 مجاناً
    return "assets/music/free_music.mp3"

with open("animals/animals_list.json") as f:
    animals = json.load(f)

def pick_animals(n=2):
    return random.sample(animals, n)

def make_script(animal):
    facts = get_animal_facts(animal["name"], count=10)
    lines = [f"{i+1}. {fact}" for i, fact in enumerate(facts)]
    lines.append("Don’t forget to subscribe and hit the bell for more!")
    return "\n".join(lines)

def generate_long_video(animal, voice_gender="male"):
    script = make_script(animal)
    voice_path = generate_voice_over(script, gender=voice_gender)
    images = get_images_for_animal(animal["name"], count=15)
    music_path = get_copyright_music(duration=120)
    clip = ImageSequenceClip(images, fps=1)
    audio = AudioFileClip(voice_path)
    music = AudioFileClip(music_path).volumex(0.3)
    final_clip = clip.set_audio(audio)
    final_clip = CompositeVideoClip([final_clip])
    out_path = f"outputs/long/{animal['name']}.mp4"
    final_clip.write_videofile(out_path, fps=24)
    return out_path

def main():
    animals_today = pick_animals(2)
    for idx, animal in enumerate(animals_today):
        gender = "male" if idx % 2 == 0 else "female"
        video = generate_long_video(animal, voice_gender=gender)
        print(f"Generated: {video}")

if __name__ == "__main__":
    main()
