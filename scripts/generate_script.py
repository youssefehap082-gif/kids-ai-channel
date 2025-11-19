import json
import random
import wikipediaapi
import openai
import google.generativeai as genai
from scripts.utils import file_tools

def select_topic():
    # Logic: Read used_animals.json, pick unused from animal_list.txt, check trending
    animals = file_tools.load_json("data/animal_list.txt") # Mock list loading
    if not animals:
        animals = ["Lion", "Eagle", "Shark", "Panda", "Wolf"]
    
    used = file_tools.load_json("data/used_animals.json")
    available = [a for a in animals if a not in used]
    
    if not available:
        # Reset used list or rotate categories
        available = animals
        
    selection = random.choice(available)
    return selection

def generate_full_script(topic):
    # Fallback Logic: OpenAI -> Gemini -> Wikipedia
    try:
        return _generate_ai_script(topic, "openai")
    except Exception:
        try:
            return _generate_ai_script(topic, "gemini")
        except Exception:
            return _generate_wiki_script(topic)

def _generate_ai_script(topic, provider):
    prompt = f"Create a viral script about {topic} for YouTube. 15 facts. Hook at start. CTA at end. JSON format."
    # Mock response for generation
    return {
        "topic": topic,
        "title": f"Why You Should Fear The {topic}",
        "description": f"Discover the insane facts about {topic}...",
        "segments": [
            {"text": f"Did you know the {topic} is an apex predator?", "keywords": [topic, "predator"]},
            {"text": "It can see in the dark.", "keywords": ["night vision", "eyes"]}
        ],
        "hashtags": ["#animals", f"#{topic}", "#nature"]
    }

def _generate_wiki_script(topic):
    wiki = wikipediaapi.Wikipedia('en')
    page = wiki.page(topic)
    summary = page.summary[0:500]
    return {
        "topic": topic,
        "title": f"Facts about {topic}",
        "description": "Educational video.",
        "segments": [{"text": s, "keywords": [topic]} for s in summary.split('. ') if s],
        "hashtags": ["#education"]
    }
