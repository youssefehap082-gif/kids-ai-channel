# tools/text_generator.py
import requests, json
from pathlib import Path

# Uses HuggingFace Inference public endpoint for small generation (gpt2) as fallback free route.
HF_API = "https://api-inference.huggingface.co/models/gpt2"

def generate_animal_facts(animal, max_facts=10):
    prompt = f"Write {max_facts} concise, interesting facts (one sentence each) about the {animal.replace('_',' ')}. Use simple clear English suitable for a broad audience."
    try:
        resp = requests.post(HF_API, headers={"Content-Type":"application/json"}, json={"inputs": prompt, "parameters":{"max_new_tokens":200}}, timeout=30)
        data = resp.json()
        if isinstance(data, dict) and data.get("error"):
            raise Exception("HF error")
        txt = ""
        if isinstance(data, list) and "generated_text" in data[0]:
            txt = data[0]["generated_text"]
        else:
            # some HF endpoints return plain text
            txt = data[0]["generated_text"] if isinstance(data, list) and data and "generated_text" in data[0] else str(data)
        # try split by sentence
        sentences = [s.strip() for s in txt.replace("\n", " ").split(".") if len(s.strip())>15]
        if len(sentences) < max_facts:
            # fallback simple facts
            sentences += [f"The {animal.replace('_',' ')} is an interesting animal." for _ in range(max_facts - len(sentences))]
        return sentences[:max_facts]
    except Exception as e:
        # fallback simple static facts
        return [f"The {animal.replace('_',' ')} is an amazing creature found in nature." for _ in range(max_facts)]
