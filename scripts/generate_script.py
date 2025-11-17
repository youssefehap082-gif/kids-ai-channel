"""
scripts/generate_script.py
Multi-provider fact generator for animals.
Returns structured dict:
{ "topic": "...", "title":"", "description":"", "facts":[..], "provider_chain":[..] }
"""
import os
import json
import logging
from typing import List, Dict, Any
from scripts.utils.http import get, post, HTTPError

logger = logging.getLogger("kids_ai.generate")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "providers_priority.json")

def load_providers():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Cannot read providers config: %s", e)
        return {"text": ["openai","wikipedia"]}

# --- provider placeholders --- #
def openai_generate(prompt: str, max_tokens=300) -> List[str]:
    """
    Minimal placeholder using OPENAI_API_KEY via HTTP or SDK.
    Replace with actual openai.ChatCompletion as required.
    """
    logger.info("openai_generate placeholder called")
    # If you have openai package: use openai.ChatCompletion.create(...) here
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    # placeholder response:
    return [f"OpenAI generated fact for prompt slice: {prompt[:100]}"]

def gemini_generate(prompt: str) -> List[str]:
    logger.info("gemini_generate placeholder called")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return [f"Gemini generated fact for: {prompt[:80]}"]

def groq_generate(prompt: str) -> List[str]:
    logger.info("groq_generate placeholder called")
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY not set")
    return [f"Groq generated fact for: {prompt[:80]}"]

def wikipedia_fallback(topic: str) -> List[str]:
    logger.info("wikipedia_fallback for topic=%s", topic)
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic.replace(" ", "_")
        r = get(url=url, timeout=10, retries=1)
        j = r.get("json") or {}
        text = j.get("extract")
        if text:
            facts = [s.strip() for s in text.split(". ") if s.strip()]
            return facts[:10]
    except Exception as e:
        logger.warning("Wikipedia failed: %s", e)
    return []

TEXT_FUNCS = {
    "openai": openai_generate,
    "gemini": gemini_generate,
    "groq": groq_generate,
    "wikipedia": wikipedia_fallback
}

def build_prompt(topic: str, style: str="viral") -> str:
    return f"Write concise engaging facts about the animal '{topic}' for an international audience. Format as short sentences."

def generate_for_topic(topic: str, n:int=10) -> Dict[str,Any]:
    providers = load_providers().get("text", ["openai","wikipedia"])
    prompt = build_prompt(topic)
    collected = []
    provider_chain = []
    for prov in providers:
        if len(collected) >= n: break
        func = TEXT_FUNCS.get(prov)
        if not func:
            logger.debug("Provider %s not implemented", prov)
            continue
        provider_chain.append(prov)
        try:
            if prov == "wikipedia":
                facts = func(topic)
            else:
                facts = func(prompt)
            for f in facts:
                s = f.strip()
                if s and s not in collected:
                    collected.append(s)
                if len(collected) >= n:
                    break
        except Exception as e:
            logger.warning("Provider %s failed: %s", prov, e)
            continue
    if len(collected) < n and "wikipedia" not in provider_chain:
        provider_chain.append("wikipedia")
        collected += wikipedia_fallback(topic)
    collected = collected[:n]
    title = f"{topic} — {len(collected)} Amazing Facts"
    description = f"Facts about {topic} — auto-generated. Sources: {', '.join(provider_chain)}"
    return {"topic": topic, "title": title, "description": description, "facts": collected, "provider_chain": provider_chain}
