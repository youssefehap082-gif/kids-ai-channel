# content_generator.py — 2025 stable version

import os
import requests
import re

# ========== API KEYS ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ========== ENDPOINTS ==========
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# =================================
# Helper: parse OpenAI/Groq response
# =================================
def extract_text(resp_json):
    try:
        return resp_json["choices"][0]["message"]["content"]
    except:
        return ""


# =================================
# Helper: clean title + facts
# =================================
def extract_title_facts(text, animal, count=10):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) == 0:
        return f"{animal.title()} Facts", []

    # title
    title = lines[0] if len(lines[0].split()) <= 12 else f"{animal.title()} Facts"

    # facts
    facts = re.split(r"(?<=[.!?])\s+", text)
    facts = [f.strip() for f in facts if len(f.strip()) > 3][:count]

    return title, facts


# =================================
# 1 — GROQ 70B (MAIN ENGINE)
# =================================
def run_groq_70b(prompt):
    if not GROQ_API_KEY:
        raise RuntimeError("NO_GROQ_KEY")

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You generate YouTube wildlife facts."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    r = requests.post(GROQ_URL, json=payload, headers=GROQ_HEADERS, timeout=40)
    if r.status_code != 200:
        raise RuntimeError(r.text)

    return extract_text(r.json())


# =================================
# 2 — GROQ 8B (backup)
# =================================
def run_groq_8b(prompt):
    if not GROQ_API_KEY:
        raise RuntimeError("NO_GROQ_KEY")

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You generate YouTube wildlife facts."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    r = requests.post(GROQ_URL, json=payload, headers=GROQ_HEADERS, timeout=40)
    if r.status_code != 200:
        raise RuntimeError(r.text)

    return extract_text(r.json())


# =================================
# 3 — GEMINI FLASH (backup2)
# =================================
def run_gemini(prompt):
    if not GEMINI_API_KEY:
        raise RuntimeError("NO_GEMINI_KEY")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 400}
    }

    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    r = requests.post(url, json=payload, timeout=40)

    if r.status_code != 200:
        raise RuntimeError(r.text)

    data = r.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return ""


# =================================
# 4 — OPENAI (last fallback)
# =================================
def run_openai(prompt):
    if not OPENAI_API_KEY:
        raise RuntimeError("NO_OPENAI")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    r = requests.post(url, json=payload, headers=headers, timeout=40)
    if r.status_code != 200:
        raise RuntimeError(r.text)

    return extract_text(r.json())


# =================================
# MASTER FUNCTION
# =================================
def generate_facts_script(animal_name, facts_count=10):

    prompt = (
        f"Write {facts_count} fun, engaging facts about {animal_name} in English. "
        "Facts should be short and interesting. "
        "Start with a short catchy title."
        "End with: 'Don't forget to subscribe and hit the bell for more!'"
    )

    errors = []

    # Try Groq 70B
    try:
        txt = run_groq_70b(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal_name, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal_name]}
    except Exception as e:
        errors.append(("GROQ_70B", str(e)))

    # Try Gemini
    try:
        txt = run_gemini(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal_name, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal_name]}
    except Exception as e:
        errors.append(("GEMINI", str(e)))

    # Try Groq 8B
    try:
        txt = run_groq_8b(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal_name, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal_name]}
    except Exception as e:
        errors.append(("GROQ_8B", str(e)))

    # Try OpenAI
    try:
        txt = run_openai(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal_name, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal_name]}
    except Exception as e:
        errors.append(("OPENAI", str(e)))

    raise RuntimeError(f"ALL_AI_FAILED: {errors}")
