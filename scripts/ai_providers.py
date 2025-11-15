# scripts/ai_providers.py
"""
AI providers abstraction used by content_generator.py.

Provides:
- ai_generate_text_scientific(animal, count)
- ai_generate_text_mixed(animal, count)
- ai_generate_text_viral(animal, count)

Behavior:
1) Try OpenAI (if OPENAI_API_KEY present)
2) On failure -> try Gemini (if GEMINI_API_KEY present)
3) On failure -> try Groq (if GROQ_API_KEY present)
4) Last fallback -> simple deterministic template-derived lines
Retries each provider a few times with exponential backoff.
"""

import os
import time
import logging
import requests
import json
from typing import List

logger = logging.getLogger("ai_providers")
logger.setLevel(logging.INFO)

OPENAI_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAIAPIKEY") or ""
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_APIKEY") or ""
GROQ_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_APIKEY") or ""


# -------------------------
# Helpers: retry + backoff
# -------------------------
def _attempt(func, retries=2, base_wait=0.5, *args, **kwargs):
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            wait = base_wait * (2 ** attempt)
            logger.warning("Attempt %d failed: %s — retrying in %.1fs", attempt + 1, e, wait)
            time.sleep(wait)
    raise last_exc


# -------------------------
# OpenAI provider
# -------------------------
def _openai_generate(prompt: str, max_tokens: int = 400) -> str:
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI key not set")
    try:
        import openai
        openai.api_key = OPENAI_KEY
        # Use the modern openai.ChatCompletion via client if available
        # For compat, try both interfaces
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            return resp["choices"][0]["message"]["content"]
        except Exception:
            # fallback to new client if installed as openai.OpenAI
            client = openai.OpenAI(api_key=OPENAI_KEY)
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0.7, max_tokens=max_tokens)
            return resp.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"OpenAI generation failed: {e}")


# -------------------------
# Gemini (Google) provider
# -------------------------
def _gemini_generate(prompt: str) -> str:
    if not GEMINI_KEY:
        raise RuntimeError("GEMINI key not set")
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-mini:generateText"
        headers = {"Content-Type": "application/json"}
        payload = {"prompt": {"messages": [{"content": prompt}]}, "temperature": 0.7}
        resp = requests.post(url + f"?key={GEMINI_KEY}", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Attempt to parse likely field paths
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0].get("content", {}).get("text", "") or data["candidates"][0].get("content", "")
        # alternative:
        return data.get("output", {}).get("text", "") or json.dumps(data)
    except Exception as e:
        raise RuntimeError(f"Gemini generation failed: {e}")


# -------------------------
# Groq provider
# -------------------------
def _groq_generate(prompt: str) -> str:
    if not GROQ_KEY:
        raise RuntimeError("GROQ key not set")
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Groq generation failed: {e}")


# -------------------------
# High-level wrapper
# -------------------------
def _generate_with_fallback(prompt: str) -> str:
    errors = []
    # 1) OpenAI
    try:
        return _attempt(_openai_generate, retries=2, base_wait=0.6, prompt=prompt)
    except Exception as e:
        logger.warning("OpenAI failed: %s", e)
        errors.append(("openai", str(e)))

    # 2) Gemini
    try:
        return _attempt(_gemini_generate, retries=1, base_wait=0.8, prompt=prompt)
    except Exception as e:
        logger.warning("Gemini failed: %s", e)
        errors.append(("gemini", str(e)))

    # 3) Groq
    try:
        return _attempt(_groq_generate, retries=1, base_wait=0.8, prompt=prompt)
    except Exception as e:
        logger.warning("Groq failed: %s", e)
        errors.append(("groq", str(e)))

    # 4) Last fallback: deterministic message (avoid hallucination)
    logger.error("All AI providers failed. Errors: %s", errors)
    return ""


# -------------------------
# Higher-level generators used by content_generator
# -------------------------
def ai_generate_text_scientific(animal: str, count: int = 8) -> List[str]:
    """
    Prompt AI for scientific, concise facts with references style.
    """
    prompt = f"""Produce {count} concise scientifically accurate facts about the {animal}. 
Each fact must be one or two sentences. Use neutral documentary tone.
If unsure, prefer conservative statements like 'species X typically...' 
Do not fabricate citations. Output as plain lines, one fact per line."""
    text = _generate_with_fallback(prompt)
    if not text:
        # deterministic fallback using safe templates
        return [f"The {animal} is a species with unique adaptations." for _ in range(count)]
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # if returned as paragraphs, split by sentences
    if len(lines) < count:
        import re
        sents = re.split(r'(?<=[.!?])\s+', text)
        lines = [s.strip() for s in sents if s.strip()]
    return lines[:count]


def ai_generate_text_mixed(animal: str, count: int = 10) -> List[str]:
    """
    Mix scientific + fun + viral phrasing.
    """
    prompt = f"""You are a creative writer for viral YouTube animal facts.
Generate {count} short facts about {animal} — mix 50% scientifically accurate statements (concise)
and 50% fun/viral phrasing. Keep lines short (1-2 sentences). No numbering.
Avoid inventing unverifiable claims."""
    text = _generate_with_fallback(prompt)
    if not text:
        return [f"{animal.capitalize()} has fascinating behaviors." for _ in range(count)]
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < count:
        import re
        sents = re.split(r'(?<=[.!?])\s+', text)
        lines = [s.strip() for s in sents if s.strip()]
    return lines[:count]


def ai_generate_text_viral(animal: str, count: int = 8) -> List[str]:
    """
    Viral-only facts: short, punchy, surprising.
    """
    prompt = f"""Write {count} viral-style, punchy facts about the {animal}. 
Keep each line extremely short (6-18 words), surprising, and shareable. No numbering."""
    text = _generate_with_fallback(prompt)
    if not text:
        return [f"{animal.capitalize()} can surprise you with its behavior." for _ in range(count)]
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < count:
        import re
        sents = re.split(r'(?<=[.!?])\s+', text)
        lines = [s.strip() for s in sents if s.strip()]
    # Trim/enforce shortness for viral style
    trimmed = []
    for l in lines:
        words = l.split()
        if len(words) > 20:
            trimmed.append(" ".join(words[:20]) + "...")
        else:
            trimmed.append(l)
    return trimmed[:count]
