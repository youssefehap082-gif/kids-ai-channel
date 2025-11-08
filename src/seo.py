def title_for(animal: str) -> str:
    return f"10 Amazing Facts About the {animal.title()} You Didn’t Know!"

def shorts_title_for(animal: str) -> str:
    return f"{animal.title()} — Mind-Blowing Fact! #Shorts"

def keywords_for(animal: str):
    core = [f"{animal} facts", f"about {animal}", f"{animal} documentary", f"{animal} info", f"{animal} habitat", f"{animal} diet"]
    return core + ["wildlife", "nature", "education", "kids learning", "science", "animals"]

def hashtags_for(animal: str, shorts=False):
    base = ["#Animals", "#Wildlife", "#Nature", "#Facts", "#Education", "#Documentary", "#AnimalFacts", "#DidYouKnow", "#Learn", "#Science"]
    if shorts: base.append("#Shorts")
    base.append(f"#{animal.title().replace(' ','')}")
    return " ".join(base[:12])

def description_for(animal: str, facts: list) -> str:
    bullets = "\n".join([f"• {f}" for f in facts])
    return (f"Discover 10 fascinating facts about the {animal.title()}!\n\n"
            f"{bullets}\n\n"
            f"Sources: open educational resources & general wildlife references.\n"
            f"Subscribe for daily animal facts!")

def tags_for(animal: str) -> list:
    return list(dict.fromkeys(keywords_for(animal)))[:15]
