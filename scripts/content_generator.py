import os, re
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_facts_script(animal_name, facts_count=10):
    prompt = (
        f"Write {facts_count} short, punchy, surprising facts about the {animal_name} "
        "(American English, 1-2 short sentences per fact). Start with a catchy 6-8 word title line. "
        "End with a single-line CTA: 'Don't forget to subscribe to WildFacts Hub for more!'"
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=450
        )
        text = resp['choices'][0]['message']['content']
    except Exception as e:
        text = f"{animal_name.title()} — Amazing Facts\n" + "\n".join([f"{i+1}. {animal_name.title()} fact {i+1}." for i in range(facts_count)]) + "\nDon't forget to subscribe to WildFacts Hub for more!"

    lines = [l.strip() for l in re.split(r'\n+', text) if l.strip()]
    title = lines[0] if lines else f"{animal_name.title()} — Amazing Facts"
    facts = []
    for l in lines[1:]:
        if len(facts) >= facts_count:
            break
        facts.append(l)
    if len(facts) < facts_count:
        sents = re.split(r'(?<=[.!?])\s+', text)
        facts = [s.strip() for s in sents if s.strip()][:facts_count]

    description = f"{title}\n\nFacts about the {animal_name}.\n" + '\n'.join([f"- {f}" for f in facts]) + "\n\n#WildFacts #Animals"
    return {
        "title": title,
        "script": "\n".join(facts),
        "description": description,
        "tags": [animal_name, "wildlife", "animals", "facts"]
    }
