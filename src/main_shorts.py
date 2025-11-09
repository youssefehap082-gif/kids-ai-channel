import os, random
from src.media_sources import get_video_urls
from src.ai_vision import is_animal_video
from src.music_picker import pick_music
from src.compose import compose_short
from src.youtube import upload_video

def main():
    print("🎬 Generating animal shorts with background music only")

    animals = ["Lion", "Tiger", "Elephant", "Panda", "Koala", "Cobra", "Dolphin", "Penguin"]
    random.shuffle(animals)

    for animal in animals[:6]:
        try:
            print(f"🎥 Creating short for {animal}")
            urls = get_video_urls(animal, limit=5)
            valid_urls = [u for u in urls if is_animal_video(u)]
            if not valid_urls:
                continue

            music = pick_music(animal)
            final = compose_short(valid_urls, music, target_duration=58)

            title = f"{animal} — Mind-Blowing Fact! #Shorts"
            desc = f"Watch this amazing short about the {animal}! 🐾\nSubscribe for more!"
            tags = [animal, "Animals", "Wildlife", "Nature"]

            upload_video(final, title, desc, tags, privacy="public")
        except Exception as e:
            print(f"⚠️ Failed to create short for {animal}: {e}")

    print("✅ All shorts generated successfully!")

if __name__ == "__main__":
    main()
