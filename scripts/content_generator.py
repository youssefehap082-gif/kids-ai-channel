# content_generator.py - produce titles, descriptions, script (10 facts)
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))


def generate_facts_script(animal_name, facts_count=10):
    prompt = (
        f"Write {facts_count} short engaging facts about the {animal_name} in simple English. "
        f"Each fact should be 1-2 sentences, interesting and surprising where possible. "
        f"Include a catchy 6-8 word title for the video at the top. "
        f"At the end add a single-line call to action: "
        f"'Don't forget to subscribe and hit the bell for more!'"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You write concise, engaging wildlife facts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=400
    )

    text = response.choices[0].message.content.strip()

    # Split lines
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = lines[0] if lines else f"{animal_name.title()} — Amazing Facts"

    # Extract facts
    facts = []
    for l in lines[1:]:
        if len(facts) >= facts_count:
            break
        facts.append(l)

    # fallback if model responded as paragraph
    if len(facts) < facts_count:
        import re
        sents = re.split(r'(?<=[.!?])\s+', text)
        facts = [s.strip() for s in sents if s.strip()][:facts_count]

    description = (
        f"{title}\n\n"
        f"Facts about the {animal_name}.\n" +
        "\n".join([f"- {f}" for f in facts]) +
        "\n\n#animals #wildlife"
    )

    return {
        "title": title,
        "script": "\n".join(facts),
        "description": description,
        "tags": [animal_name, "wildlife", "animals"]
    }
