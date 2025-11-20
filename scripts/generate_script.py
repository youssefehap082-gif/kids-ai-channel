import os
import json
import random
import logging
import google.generativeai as genai

def select_topic():
    topics = ["Lion", "Eagle", "Shark", "Wolf", "Tiger", "Bear", "Crocodile", "Elephant"]
    return random.choice(topics)

def generate_full_script(topic):
    logging.info(f"Generating AI Script for: {topic}")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Updated Model Name
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are a professional YouTube scriptwriter. Create a viral script about "{topic}".
            Output strictly valid JSON with this structure:
            {{
                "topic": "{topic}",
                "title": "...",
                "description": "...",
                "hashtags": ["#tag1"],
                "segments": [
                    {{"text": "sentence 1", "keywords": ["{topic} run"]}},
                    {{"text": "sentence 2", "keywords": ["{topic} hunt"]}}
                ]
            }}
            """
            response = model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logging.error(f"Gemini Error: {e} -> Using Fallback.")
    
    # Fallback Template
    return {
        "topic": topic,
        "title": f"10 Amazing Facts About {topic}",
        "description": f"Learn about {topic}...",
        "hashtags": ["#animals", f"#{topic}"],
        "segments": [
            {"text": f"The {topic} is a powerful creature found in nature.", "keywords": [topic]},
            {"text": "They are known for their incredible speed and agility.", "keywords": [f"{topic} running"]},
            {"text": "Scientists have studied their behavior for decades.", "keywords": [f"{topic} wild"]},
            {"text": "Their hunting skills are unmatched in the animal kingdom.", "keywords": [f"{topic} hunting"]},
            {"text": "Subscribe to our channel for more animal facts.", "keywords": ["nature landscape"]}
        ]
    }