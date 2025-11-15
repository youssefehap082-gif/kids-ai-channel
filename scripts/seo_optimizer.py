# scripts/seo_optimizer.py

import random
import logging

logger = logging.getLogger("seo")
logger.setLevel(logging.INFO)

# ------------------------------------------------------
# Helpers
# ------------------------------------------------------

VIRAL_ADJ = [
    "Amazing",
    "Mind-Blowing",
    "Unbelievable",
    "Rare",
    "Stunning",
    "Crazy",
    "Scientific",
    "Wild",
    "Incredible",
    "Fascinating"
]

HOOKS = [
    "You won’t believe fact #3!",
    "Most people don’t know this.",
    "Prepare to be shocked.",
    "Scientists recently discovered this.",
    "This blew my mind.",
]

CTA = [
    "Subscribe for more wildlife facts!",
    "Don’t forget to like and share!",
    "Support us by subscribing.",
    "More amazing animal videos coming!",
]

HASHTAGS_BASE = [
    "#animals", "#wildlife", "#nature", "#facts",
    "#animalfacts", "#documentary", "#viral",
    "#shorts", "#fyp", "#wildplanet", "#discover"
]

# ------------------------------------------------------
# Title Generator
# ------------------------------------------------------

def generate_title(animal_name: str, facts: list, mode="long"):
    """
    mode: "long" or "short"
    """
    adj = random.choice(VIRAL_ADJ)

    if mode == "long":
        return f"{adj} Facts About the {animal_name.title()} You Never Knew"
    else:
        return f"{adj} {animal_name.title()} Fact You Must Hear!"

# ------------------------------------------------------
# Description Generator
# ------------------------------------------------------

def generate_description(animal_name: str, facts: list, mode="long"):
    first_fact = facts[0] if facts else f"Learn facts about {animal_name}."

    hook = random.choice(HOOKS)
    cta = random.choice(CTA)

    desc = []
    desc.append(f"Discover amazing facts about the {animal_name.title()}.\n")
    desc.append(f"Highlight: {first_fact}\n")
    desc.append("More facts inside the video. Enjoy!\n")
    desc.append(f"{hook}\n\n")
    desc.append("––––––––––––––––––––––––––––––––––––––\n")
    desc.append("Support the channel:\n")
    desc.append(f"{cta}\n\n")
    desc.append("––––––––––––––––––––––––––––––––––––––\n")
    desc.append("Keywords:\n")
    keywords = ", ".join([
        f"{animal_name} facts",
        f"about {animal_name}",
        f"{animal_name} information",
        f"wild {animal_name}",
        f"{animal_name} documentary"
    ])
    desc.append(keywords + "\n\n")

    desc.append("––––––––––––––––––––––––––––––––––––––\n")
    desc.append("Tags / Hashtags:\n")
    desc.append(" ".join(generate_hashtags(animal_name)) + "\n")

    return "".join(desc)

# ------------------------------------------------------
# Hashtags Generator
# ------------------------------------------------------

def generate_hashtags(animal_name: str):
    h = HASHTAGS_BASE.copy()
    h.append(f"#{animal_name}")
    h.append(f"#{animal_name}facts")
    return list(dict.fromkeys(h))  # remove duplicates

# ------------------------------------------------------
# Full SEO bundle
# ------------------------------------------------------

def generate_seo(animal_name: str, facts: list, mode="long"):
    """
    Returns: title, description, hashtags
    """
    logger.info("Generating SEO for %s", animal_name)
    title = generate_title(animal_name, facts, mode)
    desc = generate_description(animal_name, facts, mode)
    tags = generate_hashtags(animal_name)

    return title, desc, tags


# Quick test
if __name__ == "__main__":
    test_facts = [
        "The lion's roar can be heard from 8 kilometers away.",
        "Lions live in groups called prides.",
        "A male lion sleeps up to 20 hours a day.",
    ]
    title, desc, tags = generate_seo("lion", test_facts, "long")
    print("TITLE:", title)
    print("DESC:\n", desc)
    print("TAGS:", tags)
