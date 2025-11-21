
import os
import json
from openai import OpenAI

def generate_script(animal_name):
    print(f"📝 Writing Viral Script for: {animal_name}")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: return None
    
    client = OpenAI(api_key=api_key)
    prompt = f'''
    Create a viral YouTube Shorts script about {animal_name}.
    Duration: 30-40 seconds.
    Style: Fast, Shocking, Engaging.
    JSON Format:
    {{
        "title": "Catchy Title Here",
        "description": "SEO description with hashtags",
        "script_text": "Full narration text here..."
    }}
    '''
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Script Error: {e}")
        return {
            "title": f"Amazing Facts about {animal_name}",
            "description": f"#shorts #{animal_name}",
            "script_text": f"Did you know the {animal_name} is one of the most interesting animals? It has unique behaviors that will shock you. Subscribe for more!"
        }
