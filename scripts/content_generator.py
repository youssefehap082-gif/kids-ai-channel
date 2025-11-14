import os, requests, re, json
from pathlib import Path

def fetch_wikipedia_extract(title, sentences=12):
    # use Wikipedia REST summary endpoint
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.requote_uri(title)}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    extract = data.get('extract')
    if not extract:
        return None
    # split into sentences
    sents = re.split(r'(?<=[.!?])\s+', extract)
    facts = [s.strip() for s in sents if s.strip()][:sentences]
    title_line = data.get('title') or title.title()
    return {'title': f"{title_line} — 10 Surprising Facts", 'facts': facts, 'source': data.get('content_urls',{}).get('desktop',{}).get('page')}

def generate_facts_script(animal_name, facts_count=10):
    # Try Wikipedia first
    wiki = fetch_wikipedia_extract(animal_name, sentences=facts_count*2)
    if wiki:
        facts = wiki['facts'][:facts_count]
        title = wiki['title']
        description = f"{title}\n\nFacts about the {animal_name}. Source: {wiki.get('source') or 'Wikipedia'}\n\n" + '\n'.join([f"- {f}" for f in facts])
        return {'title': title, 'script': '\n'.join(facts), 'description': description, 'tags': [animal_name, 'wildlife', 'animals']}
    # Fallback: simple templates
    facts = [f"{animal_name.title()} fact {i+1}." for i in range(facts_count)]
    title = f"{animal_name.title()} — {facts_count} Facts You Must Know"
    description = f"{title}\n\n" + '\n'.join([f"- {f}" for f in facts])
    return {'title': title, 'script': '\n'.join(facts), 'description': description, 'tags': [animal_name, 'wildlife', 'animals']}
