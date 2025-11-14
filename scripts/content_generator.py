# content_generator.py - produce titles, descriptions, script (10 facts)
import openai
from pathlib import Path
from datetime import datetime
import os

openai.api_key = os.getenv('OPENAIAPIKEY')

def generate_facts_script(animal_name, facts_count=10):
    prompt = f"Write {facts_count} short engaging facts about the {animal_name} in simple English. Each fact should be 1-2 sentences, interesting and surprising where possible. Include a catchy 6-8 word title for the video at the top. At the end add a single-line call to action: 'Don't forget to subscribe and hit the bell for more!'"
    resp = openai.ChatCompletion.create(
        model='gpt-4o-mini',
        messages=[{"role":"user","content":prompt}],
        temperature=0.7,
        max_tokens=400
    )
    text = resp['choices'][0]['message']['content']
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = lines[0] if lines else f'{animal_name.title()} — Amazing Facts'
    facts = []
    for l in lines[1:]:
        if len(facts) >= facts_count:
            break
        facts.append(l)
    if len(facts) < facts_count:
        import re
        sents = re.split(r'(?<=[.!?])\s+', text)
        facts = [s.strip() for s in sents if s.strip()][:facts_count]

    description = f"{title}\n\nFacts about the {animal_name}.\n" + '\n'.join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
    return {
        'title': title,
        'script': '\n'.join(facts),
        'description': description,
        'tags': [animal_name, 'wildlife', 'animals']
    }
