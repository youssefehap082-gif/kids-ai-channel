import os, requests, re
from pathlib import Path
from .utils import read_json
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
def _openai_chat(prompt):
    if not OPENAI_KEY: raise RuntimeError('OPENAI key missing')
    url = 'https://api.openai.com/v1/chat/completions'
    payload = {'model':'gpt-4o-mini','messages':[{'role':'user','content':prompt}],'temperature':0.7,'max_tokens':400}
    r = requests.post(url, json=payload, headers={'Authorization':f'Bearer {OPENAI_KEY}'}, timeout=30)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']
def generate_facts_script(animal_name, facts_count=10):
    prompt = f'Write {facts_count} short engaging facts about the {animal_name} in simple English. Each fact 1-2 sentences. Start with a 6-word catchy title line.'
    try:
        text = _openai_chat(prompt)
    except Exception as e:
        # fallback to DB summary
        db = read_json(Path(__file__).resolve().parent.parent / 'data' / 'animal_database.json') or []
        for a in db:
            if a.get('name') == animal_name and a.get('facts'):
                facts = a['facts'][:facts_count]
                title = f'{animal_name.title()} — Facts'
                return {'title':title,'script':'\n'.join(facts),'description':title,'tags':[animal_name,'wildlife']}
        raise
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = lines[0] if lines else f'{animal_name} — Facts'
    facts = []
    for l in lines[1:]:
        if len(facts) >= facts_count: break
        facts.append(l)
    if len(facts) < facts_count:
        sents = re.split(r'(?<=[.!?])\s+', text)
        facts = [s.strip() for s in sents if s.strip()][:facts_count]
    desc = f'{title}\n\n' + '\n'.join([f'- {f}' for f in facts])
    return {'title':title,'script':'\n'.join(facts),'description':desc,'tags':[animal_name,'wildlife']}
