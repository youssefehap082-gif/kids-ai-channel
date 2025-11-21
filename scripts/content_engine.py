import random

def generate_script(animal_name):
    print(f"📝 Writing Script using FREE Template for: {animal_name}")
    
    # Database of facts
    facts_db = {
        "Red Panda": [
            "Red Pandas use their bushy tails as blankets in winter.",
            "They are the original Panda, discovered before the Giant Panda!",
            "They consume 200,000 bamboo leaves every day."
        ],
        "Lion": [
            "A lion's roar can be heard from 5 miles away.",
            "Lions sleep for up to 20 hours a day.",
            "Females do 90 percent of the hunting."
        ]
    }
    
    facts = facts_db.get(animal_name, [
        f"{animal_name} is an amazing creature.",
        f"Scientists are still discovering secrets about the {animal_name}.",
        "Nature is truly wonderful."
    ])
    
    script_text = f"Did you know these facts about the {animal_name}? {facts[0]} {facts[1]} {facts[2]} Subscribe for more animal facts!"
    
    return {
        "title": f"Shocking Facts about {animal_name} 😱 #shorts",
        "description": f"Amazing facts about {animal_name}. #shorts #animals #nature",
        "script_text": script_text
    }
