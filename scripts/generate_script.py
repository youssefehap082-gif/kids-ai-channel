"""
scripts/generate_script.py
Multi-provider fact generator.
- Tries providers from providers_priority.json (text order)
- Falls back to Wikipedia if providers fail.
- Returns: dict { facts: [..], provider_chain: [...], metadata: {...} }
"""

import os
import json
import logging
from typing import List, Dict, Any

from scripts.utils.http import get, post, HTTPError

logger = logging.getLogger("kids_ai.generate")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(ch)


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "providers_priority.json")
# providers_priority.json example:
# { "text": ["openai","gemini","groq","wikipedia"], "tts": [...], "media": [...] }


def load_providers_config(path=CONFIG_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to load providers config %s: %s", path, e)
        # default fallback
        return {"text": ["openai", "wikipedia"]}


# --- provider implementations (minimal placeholders) --- #
def provider_openai_generate(prompt: str, api_key: str, max_tokens=300) -> List[str]:
    """
    Placeholder minimal OpenAI text call.
    Replace with your preferred sdk usage (openai.ChatCompletion or OpenAI client).
    """
    # Keep it minimal but representative (no external openai import here to avoid dependency)
    logger.info("Calling OpenAI (placeholder) for prompt length=%d", len(prompt))
    # TODO: replace with real openai.Completion.create / chat completion
    return [f"OpenAI-fake-fact for prompt: {prompt[:80]}"]


def provider_gemini_generate(prompt: str, api_key: str) -> List[str]:
    logger.info("Calling Gemini (placeholder)")
    return [f"Gemini-fake-fact for prompt: {prompt[:80]}"]


def provider_groq_generate(prompt: str, api_key: str) -> List[str]:
    logger.info("Calling Groq (placeholder)")
    return [f"Groq-fake-fact for prompt: {prompt[:80]}"]


def provider_wikipedia_search(topic: str, limit=10) -> List[str]:
    """
    Simple Wikipedia fallback: use REST wiki API to get intro paragraphs.
    """
    logger.info("Wikipedia fallback search for topic=%s", topic)
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic.replace(" ", "_")
        r = get(url=url, timeout=10, retries=1)
        j = r.get("json") or {}
        # j may contain 'extract' with summary
        text = j.get("extract")
        if text:
            # naive split into sentences, but we can split facts by lines
            facts = [s.strip() for s in text.split(". ") if s.strip()]
            return facts[:10]
    except Exception as e:
        logger.warning("Wikipedia lookup failed: %s", e)
    return []


# map names -> functions
TEXT_PROVIDERS_MAP = {
    "openai": provider_openai_generate,
    "gemini": provider_gemini_generate,
    "groq": provider_groq_generate,
    "wikipedia": provider_wikipedia_search
}


def generate_facts(topic: str, desired=10) -> Dict[str, Any]:
    """
    Orchestrate multi-provider generation and fallback until we collect 'desired' facts.
    Returns: { facts: [...], provider_chain: [...], used_provider: str, notes: {...} }
    """
    providers = load_providers_config().get("text", ["openai", "wikipedia"])
    logger.info("Provider priority for text: %s", providers)

    collected = []
    provider_chain = []

    # prompt template
    prompt = f"Give concise factual sentences about the topic '{topic}'. Provide clear, verifiable facts suitable for an educational YouTube video. Number them."
    for prov in providers:
        if len(collected) >= desired:
            break
        func = TEXT_PROVIDERS_MAP.get(prov)
        if not func:
            logger.debug("Provider %s not implemented, skipping", prov)
            continue
        provider_chain.append(prov)

        # obtain API key from env (if provider needs it)
        api_key = os.environ.get(f"{prov.upper()}_API_KEY") or os.environ.get("OPENAI_API_KEY")
        try:
            if prov == "wikipedia":
                facts = func(topic)
            else:
                facts = func(prompt, api_key=api_key)
            if not facts:
                logger.warning("Provider %s returned no facts", prov)
                continue
            # normalize and append unique
            for f in facts:
                s = f.strip()
                if s and s not in collected:
                    collected.append(s)
                if len(collected) >= desired:
                    break
        except Exception as e:
            logger.exception("Provider %s failed: %s", prov, e)
            continue

    # final fallback: if still empty, try Wikipedia by topic
    if len(collected) < desired and "wikipedia" not in provider_chain:
        provider_chain.append("wikipedia")
        collected += provider_wikipedia_search(topic)

    # trim to desired
    collected = collected[:desired]

    return {
        "facts": collected,
        "provider_chain": provider_chain,
        "count": len(collected),
        "topic": topic
    }


# allow running standalone
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True)
    p.add_argument("--n", type=int, default=10)
    args = p.parse_args()
    out = generate_facts(args.topic, desired=args.n)
    print(json.dumps(out, indent=2, ensure_ascii=False))
