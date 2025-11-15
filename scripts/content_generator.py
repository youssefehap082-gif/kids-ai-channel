import os
import random
import json
import logging
from pathlib import Path

import requests
from scripts.fetch_wikipedia import fetch_wiki_facts

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------
# AVAILABLE MODES:
# scientific  → حقائق علمية دقيقة
# mixed       → علمية + ممتعة (الأفضل للمشاهدة)
# viral       → حقائق صادمة/ممتعة بأسلوب تيك توك
# --------------------------------------------------------------

# ==========================
# AI PROVIDERS
# ==========================

def ai_openai(prompt):
    import openai

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert documentary writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return resp.choices[0].message["content"]
    except Exception as e:
        return None


def ai_groq(prompt):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "Expert animal fact generator."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 700
            },
            timeout=20
        )
        j = r.json()
        return j["choices"][0]["message"]["content"] if "choices" in j else None
    except:
        return None


def ai_gemini(prompt):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=data, timeout=20)
        j = r.json()
        return j["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return None


def ai_hf(prompt):
    key = os.getenv("HF_API_TOKEN")
    if not key:
        return None
    try:
        r = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers={"Authorization": f"Bearer {key}"},
            json={"inputs": prompt},
            timeout=20
        )
        return r.json()[0]["generated_text"]
    except:
        return None


def fallback_simple(prompt):
    """آخر حل، مولد نص عادي لو كل AI providers فشلوا"""
    return f"{prompt}\nHere are simplified facts:\n1. This animal is interesting.\n2. It lives in the wild.\n3. It has unique behaviors.\n4. This fact is auto-generated.\n5. Enjoy learning!"


AI_PROVIDERS = [
    ("openai", ai_openai),
    ("groq", ai_groq),
    ("gemini", ai_gemini),
    ("hf", ai_hf),
    ("fallback", fallback_simple),
]


# =====================================================
#  CONTENT GENERATOR
# =====================================================

def build_prompt(animal, style, wiki_facts):
    """Generate master prompt"""

    base = f"Write {10 if style!='viral' else 5} facts about the animal '{animal}'."

    if style == "scientific":
        tone = "scientific, accurate, documentary, wildlife journal style"
    elif style == "mixed":
        tone = "mixed: 70% scientific + 30% fun, engaging, human-friendly"
    else:
        tone = "viral, shocking, fun, TikTok style, very engaging but still true"

    prompt = f"""
You are an expert wildlife documentary writer.

Animal: {animal}

Tone: {tone}

Wikipedia reference facts:
{wiki_facts}

Write:
- Title (engaging)
- Description (2–5 lines)
- Tags (10 keywords)
- Facts in bullet points
- Then write a final long transcript (1 paragraph)
"""

    return prompt


def parse_ai_response(text, animal):
    """Extract fields from AI output"""
    try:
        lines = text.splitlines()
        title = next((l for l in lines if "title" in l.lower()), f"Facts about {animal}")
    except:
        title = f"Facts about {animal}"

    description = text[:4000] if len(text) > 20 else f"Interesting facts about {animal}."

    tags = [animal, "animals", "wildlife", "facts"]

    # extract facts
    facts = []
    for line in text.split("\n"):
        if line.strip().startswith("-") or line.strip()[0:2] == "1.":
            facts.append(line.strip("-• "))

    if not facts:
        facts = [f"{animal} is interesting."]

    transcript = "\n".join(facts)

    return {
        "title": title.replace("Title:", "").strip(),
        "description": description,
        "tags": tags,
        "facts": facts,
        "transcript": transcript,
    }


def generate_facts_script(
    animal,
    num_facts_long=10,
    num_facts_short=1,
    style="mixed"
):
    """
    Main content generator with full AI fallback
    """
    logger.info(f"Generating script for {animal} ({style})")

    # 1) fetch Wikipedia scientific facts
    try:
        wiki_facts = fetch_wiki_facts(animal)
    except Exception as e:
        logger.warning("Wikipedia fetch failed: %s", e)
        wiki_facts = "No scientific reference available."

    prompt = build_prompt(animal, style, wiki_facts)

    errors = []
    result_text = None

    # try all AI providers one by one
    for name, provider in AI_PROVIDERS:
        logger.info(f"Trying AI provider: {name}")
        try:
            out = provider(prompt)
            if out and len(out) > 30:
                result_text = out
                break
        except Exception as e:
            errors.append((name, str(e)))

    if not result_text:
        raise RuntimeError(f"ALL AI FAILED for {animal}: {errors}")

    # Parse output
    parsed = parse_ai_response(result_text, animal)

    script_long = "\n".join(parsed["facts"][:num_facts_long])
    script_short = "\n".join(parsed["facts"][:num_facts_short])

    return (
        {
            "title": parsed["title"],
            "description": parsed["description"],
            "tags": parsed["tags"],
            "facts": parsed["facts"],
        },
        script_long if num_facts_long > 1 else script_short,
    )
