import os
import re
import tempfile
import random
import json

def get_trending_animals():
    """Fake trending animals generator until API is ready"""
    animals = [
        "Lion", "Elephant", "Tiger", "Panda", "Shark", "Giraffe",
        "Cheetah", "Zebra", "Kangaroo", "Dolphin", "Koala"
    ]
    random.shuffle(animals)
    return animals[:6]

def get_video_stats_bulk():
    """Fake stats for now — return random engagement to simulate analytics"""
    stats = {}
    for animal in get_trending_animals():
        stats[animal] = {
            "views": random.randint(1000, 50000),
            "likes": random.randint(50, 3000),
            "comments": random.randint(0, 400)
        }
    return stats

def safe_filename(animal):
    safe = re.sub(r"\W+", "_", animal.lower())
    return safe

def make_temp_thumb(animal):
    path = os.path.join(tempfile.gettempdir(), f"thumb_{safe_filename(animal)}.png")
    return path
