# scripts/content_generator.py

import wikipedia
import random
import logging

log = logging.getLogger("content_generator")


def fetch_scientific_facts(animal, max_facts=10):
    """Fetch scientific facts from Wikipedia (clean + simple)."""
    try:
        summary = wikipedia.summary(animal, sentences=5, auto_suggest=True)
        paragraphs = summary.split(". ")
        facts = [p.strip() for p in paragraphs if len(p.strip()) > 20]
        return facts[:max_facts]
    except Exception as e:
        log.error(f"Wikipedia fetch failed for {animal}: {e}")
        return []


def generate_fun_facts(animal, max_facts=10):
    """Viral-style fun facts."""
    base = [
        f"Did you know? The {animal} is one of the most unique creatures on Earth.",
        f"The {animal} has secret behaviors most people never hear about.",
        f"Scientists discovered something unusual about the {animal}.",
        f"Many people don't know this shocking fact about the {animal}.",
        f"The {animal} has survival abilities that surprise even experts.",
        f"Here’s a mind-blowing fact about {animal}.",
    ]
    random.shuffle(base)
    return base[:max_facts]


def generate_viral_facts(animal, max_facts=10):
    """TikTok style punchy facts."""
    viral = [
        f"The {animal} can do something you won't believe.",
        f"This {animal} fact is almost impossible to believe.",
        f"Most people get shocked when they hear this about {animal}.",
        f"The {animal} hides a secret ability.",
        f"You've never seen a {animal} fact like this.",
    ]
    random.shuffle(viral)
    return viral[:max_facts]


def combine_facts(scientific, fun, viral, pick=10):
    all_facts = scientific + fun + viral
    random.shuffle(all_facts)
    return all_facts[:pick]


def generate_facts_script(
    animal,
    num_facts_long=10,
    num_facts_short=1
):
    """Generate both long and short video scripts."""

    scientific = fetch_scientific_facts(animal, max_facts=num_facts_long)
    fun = generate_fun_facts(animal, max_facts=num_facts_long)
    viral = generate_viral_facts(animal, max_facts=num_facts_long)

    combined = combine_facts(scientific, fun, viral, pick=num_facts_long)

    # long script
    long_script = f"Here are {num_facts_long} amazing facts about the {animal}:\n"
    for i, fact in enumerate(combined, 1):
        long_script += f"{i}. {fact}\n"

    # short script (1 fact)
    short_fact = combined[0] if combined else "A unique animal with amazing behavior."
    short_script = f"{short_fact}"

    return long_script, combined
