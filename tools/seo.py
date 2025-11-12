# tools/seo.py
def make_title_description_tags(animal, facts):
    name = animal.replace("_"," ").title()
    title = f"10 Amazing Facts About the {name} | Animal Facts"
    # brief description with keywords
    desc = f"Discover 10 amazing facts about the {name}. Learn about behavior, habitat, diet and unique traits. Perfect for nature lovers and educators."
    tags = [name, "animal facts", "wildlife", "animals", "facts", f"{name} facts"]
    return title, desc, tags
