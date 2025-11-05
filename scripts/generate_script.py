# generates a JSON-like script for one episode using Hugging Face text model
import os, requests, json
HF_TOKEN = os.environ.get("HF_API_TOKEN")
MODEL = "gpt2"  # لو تحب استخدم موديل أقوى لو متاح

prompt = """
Write a children's story episode in English (characters: Hazem and Sheh Madwar).
Length ~6 minutes (about 800 words). Output JSON with fields:
{ "title": "...", "scenes": [ {"time":"0:00","voice":"...","image_prompt":"..."} ... ] }
Make it family friendly and end with: "Subscribe for the next episode".
"""
resp = requests.post(
    f"https://api-inference.huggingface.co/models/{MODEL}",
    headers={"Authorization": f"Bearer {HF_TOKEN}"},
    json={"inputs": prompt, "options":{"wait_for_model":True}}
)
resp.raise_for_status()
out = resp.text
open("output/script_raw.txt","w",encoding="utf-8").write(out)
print("Saved output/script_raw.txt — open and edit to adjust scenes/prompts.")
