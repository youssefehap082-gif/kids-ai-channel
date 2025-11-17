import random

FACTS = [
    "Did you know? Cats sleep for 70% of their lives.",
    "Fun Fact: Honey never spoils, ever!",
    "Cool Fact: Octopuses have 3 hearts.",
    "Mind-blowing: Bananas are berries, but strawberries aren't!",
    "Wild Fact: A shrimp's heart is in its head.",
]


def generate_facts():
    """Return a random educational fun fact."""
    return random.choice(FACTS)
