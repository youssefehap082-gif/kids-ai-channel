# scripts/seo_optimizer.py
"""
Builds SEO-optimized titles, descriptions, and tags.
Simple heuristics:
- title: "10 Facts about {animal} | Amazing {animal} Facts"
- description: includes facts summary + CTA + keywords
- tags: animal + variations + 'animals','wildlife','facts'
"""
import random
def build_title_desc_hashtags(animal, facts_list, long=True):
    animal_cap = animal.title()
    if long:
        title = f"10 Amazing Facts About the {animal_cap} | Wildlife Facts"
    else:
        title = f"Quick {animal_cap} Fact — Did You Know?"

    # description: take top 3 facts
    snippet = " ".join((facts_list[:3] if facts_list else ["Amazing animal facts."]))
    description = f"{title}\n\n{snippet}\n\nSubscribe for more wildlife facts! Don't forget to hit the bell.\n\n#animals #wildlife #{animal.replace(' ', '')}"

    # tags (limit to 50)
    tags = [animal.lower().replace(' ', '_'), "animals", "wildlife", "facts"]
    # add a few variations
    tags += [animal.split()[0].lower() if " " in animal else animal.lower(), "animal facts"]
    tags = list(dict.fromkeys(tags))[:50]
    return title, description, tags
