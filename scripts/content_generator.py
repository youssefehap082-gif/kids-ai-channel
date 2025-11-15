# scripts/content_generator.py

import os
import json
import random
from scripts.fetch_wikipedia import fetch_wiki_facts

from openai import OpenAI
import requests

# ========= LOAD KEYS ==========
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_KEY   = os.getenv("GROQ_API_KEY", "")


# -------------------------------
#   FALLBACK AI SYSTEM
# -------------------------------
def ai_generate(prompt):
    """
    يحاول 4 نماذج بالترتيب:
    1) OpenAI GPT (الأفضل)
    2) Gemini
    3) Groq (Llama)
    4) Local Mini Model (dummy)
    """

    errors = []

    # 1) OpenAI
    if OPENAI_KEY:
        try:
            client = OpenAI(api_key=OPENAI_KEY)
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return r.choices[0].message.content
        except Exception as e:
            errors.append(("openai", str(e)))

    # 2) Gemini
    if GEMINI_KEY:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_KEY
            r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]})
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            errors.append(("gemini", str(e)))

    # 3) Groq
    if GROQ_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}"}
            r = requests.post(url, headers=headers, json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
            })
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            errors.append(("groq", str(e)))

    # 4) آخر حل – mini model
    errors.append(("local-mini", "fallback used"))
    return "No AI available — fallback text."


# ---------------------------------------
#             SCRIPT BUILDER
# ---------------------------------------
def build_scientific_facts(animal, wiki_facts):
    return wiki_facts[:8]


def build_viral_facts(animal):
    prompt = f"""
Give me 12 viral-style facts about {animal}.
Make them surprising, fun, emotional, and TikTok style.
Short lines. No numbering.
"""
    txt = ai_generate(prompt)
    lines = [l.strip() for l in txt.split("\n") if len(l.strip()) > 4]
    return lines[:10]


def build_mixed_facts(animal, wiki_facts):
    prompt = f"""
You are a YouTube viral animal expert.

Generate 10 MIXED facts about {animal}.
50% scientific accurate + 50% fun / emotional / shocking.

Short lines, no numbering.
"""
    ai_txt = ai_generate(prompt)
    ai_facts = [l.strip() for l in ai_txt.split("\n") if len(l.strip()) > 4]

    combined = wiki_facts[:5] + ai_facts[:5]
    return combined


# ------------------------------------------------------
#     MAIN — Generate Full Script (Long + Short)
# ------------------------------------------------------
def generate_facts_script(animal_name,
                          num_facts_long=10,
                          num_facts_short=1):

    # 1) ويكيبيديا
    wiki_facts = fetch_wiki_facts(animal_name)

    if not wiki_facts:
        wiki_facts = [f"{animal_name} is a fascinating creature with unique behavior."]

    # 2) Scientific
    scientific = build_scientific_facts(animal_name, wiki_facts)

    # 3) Viral
    viral = build_viral_facts(animal_name)

    # 4) Mixed
    mixed = build_mixed_facts(animal_name, wiki_facts)

    # ========== LONG VIDEO SCRIPT ==========
    long_script = []
    long_script.extend(scientific[:4])
    long_script.extend(mixed[:4])
    long_script.extend(viral[:4])

    random.shuffle(long_script)

    long_script = long_script[:num_facts_long]

    # ========== SHORT SCRIPT (VERY SHORT FACT) ==========
    if num_facts_short == 1:
        # خليه صادم وممتع
        short_script = viral[:1]
    else:
        short_script = viral[:num_facts_short]

    return long_script, short_script
