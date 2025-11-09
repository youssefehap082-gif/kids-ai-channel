import os, random, requests

def pick_music(animal_name: str) -> str:
    """
    Picks background music based on the animal mood.
    Returns local path to downloaded mp3.
    """
    print(f"🎵 Selecting music for {animal_name}")

    mood = "calm"
    if any(word in animal_name.lower() for word in ["lion", "cobra", "tiger", "dragon"]):
        mood = "epic"
    elif any(word in animal_name.lower() for word in ["turtle", "panda", "dolphin"]):
        mood = "soft"

    apis = [
        ("pixabay", "https://pixabay.com/api/audio/?key=" + os.getenv("PIXABAY_API_KEY") + f"&q={mood}"),
        ("coverr", f"https://api.coverr.co/tracks?search={mood}"),
        ("storyblocks", f"https://api.storyblocks.com/api/v2/media/search?term={mood}&media_type=music&api_key={os.getenv('STORYBLOCKS_API_KEY')}"),
        ("vecteezy", f"https://www.vecteezy.com/api/v1/audio?q={mood}&api_key={os.getenv('VECTEEZY_API_KEY')}")
    ]

    random.shuffle(apis)
    for name, url in apis:
        try:
            res = requests.get(url, timeout=15)
            data = res.json()
            mp3_url = None

            if name == "pixabay":
                mp3_url = data["hits"][0]["audio"]
            elif name == "coverr":
                mp3_url = data["tracks"][0]["preview"]
            elif name == "storyblocks":
                mp3_url = data["results"][0]["media_url"]
            elif name == "vecteezy":
                mp3_url = data["data"][0]["url"]

            if mp3_url:
                path = f"/tmp/{animal_name.replace(' ', '_')}_music.mp3"
                r = requests.get(mp3_url)
                with open(path, "wb") as f:
                    f.write(r.content)
                print(f"✅ Picked {name} music: {mp3_url}")
                return path
        except Exception as e:
            print(f"⚠️ Music source {name} failed: {e}")

    print("⚠️ No music found, skipping music.")
    return None
