
import requests, json

def generate_animal_facts(animal):
    prompt = f"Write 10 interesting and fun facts about the animal {animal}. Each fact should be one sentence in simple English."
    resp = requests.post("https://api-inference.huggingface.co/models/gpt2",
                         headers={"Content-Type": "application/json"},
                         data=json.dumps({"inputs": prompt}))
    try:
        txt = resp.json()[0]["generated_text"]
    except Exception:
        txt = f"Interesting facts about {animal}: It is unique, it moves, it eats, it lives in nature."
    lines = [l.strip() for l in txt.split(".") if len(l.strip()) > 15][:10]
    if len(lines) < 10:
        lines += [f"{animal.title()} is an amazing creature found in nature." for _ in range(10 - len(lines))]
    return lines
