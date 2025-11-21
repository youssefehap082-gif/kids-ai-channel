
import os
import json
from openai import OpenAI

def generate_script(animal_name):
    print(f"📝 Generating Script for: {animal_name}")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = f'''
    Topic: {animal_name}
    Style: Viral YouTube Shorts.
    Structure: Hook, Intro, 3 Facts, Outro.
    Output: JSON keys: hook, intro, facts (list), outro.
    '''
    try:
        # Mock response for testing if API fails or credits low
        # Remove this mock block to use real API
        return {
            "hook": f"Did you know {animal_name} can do this?",
            "intro": "Welcome to Animal Facts.",
            "facts": ["Fact 1 is crazy.", "Fact 2 is wild.", "Fact 3 is wow."],
            "outro": "Subscribe for more!"
        }
    except Exception as e:
        print(f"❌ Script Gen Failed: {e}")
        return None
