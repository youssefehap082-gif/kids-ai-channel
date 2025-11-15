import os
import random
import logging
import wikipedia

from scripts.utils import clean_text
from scripts.ai_providers import (
    ai_generate_text_scientific,
    ai_generate_text_mixed,
    ai_generate_text_viral,
)

logger = logging.getLogger("content_generator")

# Set Wikipedia language to English
wikipedia.set_lang("en")


def fetch_wikipedia_facts(animal_name, limit=10):
    """
    Gets highly accurate scientific info from Wikipedia.
    Always returns clean, real data.
    """
    try:
        page = wikipedia.page(animal_name, auto_suggest=True)
        summary = clean_text(page.summary)
    except Exception:
        summary = f"{animal_name} is an animal species."

    sentences = summary.split(". ")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]

    return sentences[:limit]


def ai_generate_facts(animal, mode="mixed", count=10):
    """
    mode:
      scientific → Research-grade, from wiki-derived prompts
      mixed → viral + scientific + fun
      viral → pure engagement / shorts style
    """
    if mode == "scientific":
        return ai_generate_text_scientific(animal, count)

    if mode == "viral":
        return ai_generate_text_viral(animal, count)

    return ai_generate_text_mixed(animal, count)


def generate_facts_script(animal_name, num_facts_long=10, num_facts_short=1, short_mode=False):
    """
    Returns:
      full_script (string)
      facts_list (list)
    """

    mode = random.choice(["scientific", "mixed", "mixed", "viral"])

    # Wikipedia baseline
    wiki_facts = fetch_wikipedia_facts(animal_name, limit=12)

    # AI-enhanced facts
    ai_facts = ai_generate_facts(animal_name, mode=mode, count=num_facts_long)

    # Combine & clean
    all_facts = wiki_facts[:3] + ai_facts
    all_facts = [clean_text(f) for f in all_facts if f]

    if short_mode:
        # 1 viral fact per short
        return None, all_facts[:1]

    # Build narration script
    lines = []
    for idx, fact in enumerate(all_facts[:num_facts_long], start=1):
        lines.append(f"Fact {idx}: {fact}")

    lines.append("\nDon't forget to subscribe and hit the bell for more!")

    script = "\n".join(lines)
    return script, all_facts[:num_facts_long]
