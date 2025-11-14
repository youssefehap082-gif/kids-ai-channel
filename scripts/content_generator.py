import os
import requests
import re

# KEYS
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ENDPOINTS
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def extract_text(resp):
    try:
        return resp["choices"][0]["message"]["content"]
    except:
        return ""


def extract_title_facts(txt, animal, count):
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    title = lines[0] if lines else f"{animal.title()} Facts"

    facts = re.split(r"(?<=[.!?])\s+", txt)
    facts = [f for f in facts if len(f) > 5][:count]

    return title, facts


# GROQ MAIN MODEL
def run_groq_main(prompt):
    if not GROQ_API_KEY:
        raise RuntimeError("NO_GROQ_KEY")

    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "You generate engaging YouTube wildlife facts."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 400,
        "temperature": 0.7
    }

    r = requests.post(GROQ_URL, json=payload, headers=GROQ_HEADERS, timeout=60)

    if r.status_code != 200:
        raise RuntimeError(r.text)

    return extract_text(r.json())


# GROQ BACKUP
def run_groq_backup(prompt):
    if not GROQ_API_KEY:
        raise RuntimeError("NO_GROQ_KEY")

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You generate engaging YouTube wildlife facts."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 400,
        "temperature": 0.7
    }

    r = requests.post(GROQ_URL, json=payload, headers=GROQ_HEADERS, timeout=60)

    if r.status_code != 200:
        raise RuntimeError(r.text)

    return extract_text(r.json())


# GEMINI BACKUP
def run_gemini(prompt):
    if not GEMINI_API_KEY:
        raise RuntimeError("NO_GEMINI_KEY")

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 400}
    }

    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    r = requests.post(url, json=payload, timeout=60)

    if r.status_code != 200:
        raise RuntimeError(r.text)

    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return ""


# OPENAI FALLBACK
def run_openai(prompt):
    if not OPENAI_API_KEY:
        raise RuntimeError("NO_OPENAI_KEY")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.7
    }

    r = requests.post(url, json=payload, headers=headers, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(r.text)

    return extract_text(r.json())


def generate_facts_script(animal, facts_count=10):

    prompt = (
        f"Write {facts_count} short, fun, educational facts about the animal '{animal}'. "
        f"Start with a strong, catchy title. "
        f"End the script with: Don't forget to subscribe and hit the bell for more!"
    )

    errors = []

    # 1 — GROQ MAIN
    try:
        txt = run_groq_main(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal]}
    except Exception as e:
        errors.append(("GROQ_MAIN", str(e)))

    # 2 — GROQ BACKUP
    try:
        txt = run_groq_backup(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal]}
    except Exception as e:
        errors.append(("GROQ_BACKUP", str(e)))

    # 3 — GEMINI
    try:
        txt = run_gemini(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal]}
    except Exception as e:
        errors.append(("GEMINI", str(e)))

    # 4 — OPENAI
    try:
        txt = run_openai(prompt)
        if txt:
            title, facts = extract_title_facts(txt, animal, facts_count)
            desc = f"{title}\n\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": desc, "tags": [animal]}
    except Exception as e:
        errors.append(("OPENAI", str(e)))

    raise RuntimeError(f"ALL_AI_FAILED: {errors}")
