import requests, os

def is_animal_video(video_url: str) -> bool:
    """
    Checks if a video is animal-related using the Replicate model.
    Returns True if animal detected, otherwise False.
    """
    print(f"🧠 Checking content of video: {video_url}")
    try:
        headers = {"Authorization": f"Token {os.getenv('REPLICATE_API_TOKEN')}"}
        json_data = {"input": {"image": video_url}}
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=json_data
        )
        result = response.json()
        labels = str(result)
        if any(word in labels.lower() for word in ["animal", "bird", "fish", "snake", "turtle", "reptile", "wildlife"]):
            print("✅ Animal detected in video")
            return True
        else:
            print("🚫 Not an animal video, skipping...")
            return False
    except Exception as e:
        print(f"⚠️ Vision check failed: {e}")
        return True  # fallback to accept
