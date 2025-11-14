# content_generator.py - produce titles, descriptions, script (10 facts)
# Multi-tier fallback:
# 1) GROQ (llama3-70b-8192) via Groq OpenAI-compatible endpoint
# 2) Gemini (google genai) if GEMINI_API_KEY present
# 3) GROQ (llama3-8b-8192)
# 4) OpenAI (if OPENAI_API_KEY present) as last resort
#
# Returns dict: { title, script, description, tags }

import os
import requests
import time
import re

# Optional OpenAI client (kept as final fallback)
try:
    from openai import OpenAI as OpenAIClient
except Exception:
    OpenAIClient = None

# Optional Google genai (Gemini)
try:
    from google import genai
    from google.genai import types as genai_types
except Exception:
    genai = None

# Config / env
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Constants
GROQ_BASE = "https://api.groq.com/openai/v1"  # Groq OpenAI-compatible base
GROQ_CHAT_ENDPOINT = f"{GROQ_BASE}/chat/completions"
TIMEOUT_SECS = 30


def _normalize_response_text_from_openai_style(resp_json):
    """
    Accepts OpenAI/Groq-style response JSON and returns text string.
    Handles choices[0].message.content OR choices[0].text
    """
    if not resp_json:
        return ""
    choices = resp_json.get("choices") or resp_json.get("outputs") or []
    if choices:
        c0 = choices[0]
        # OpenAI/Groq chat style
        msg = c0.get("message") or c0.get("delta") or c0.get("message")
        if isinstance(msg, dict):
            content = msg.get("content") or msg.get("content", {}).get("text") or msg.get("text")
            if isinstance(content, dict):
                # sometimes nested
                return content.get("text", "").strip()
        # common fields
        if "message" in c0 and isinstance(c0["message"], dict):
            m = c0["message"]
            # sometimes the content is in m['content'] which could be a str or list
            if isinstance(m.get("content"), str):
                return m.get("content").strip()
            if isinstance(m.get("content"), list) and m["content"]:
                # join if list
                return " ".join([p.get("text", "") for p in m["content"] if isinstance(p, dict)]).strip()
        # fallback to text field
        if c0.get("text"):
            return c0.get("text").strip()
        # some Groq responses put text at choices[0].message.content
        if isinstance(c0.get("message"), dict):
            # openai-compatible
            inner = c0["message"].get("content")
            if isinstance(inner, str):
                return inner.strip()
            if isinstance(inner, list) and inner:
                return " ".join([chunk.get("text", "") for chunk in inner if isinstance(chunk, dict)]).strip()
    # fallback try top-level 'text'
    if isinstance(resp_json.get("text"), str):
        return resp_json.get("text").strip()
    return ""


def _extract_title_and_facts(text, animal_name, facts_count):
    # Expect model returns title as first line then facts; handle gracefully.
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = None
    facts = []
    if lines:
        # Heuristic: first short line is title if <= 12 words
        if len(lines[0].split()) <= 12:
            title = lines[0]
            rest = "\n".join(lines[1:])
        else:
            rest = "\n".join(lines)
        # try to split into sentences
        sents = re.split(r'(?<=[.!?])\s+', rest)
        for s in sents:
            s = s.strip()
            if s:
                facts.append(s)
            if len(facts) >= facts_count:
                break
    # fallback generation if missing
    if not title:
        title = f"{animal_name.title()} — Amazing Facts"
    if len(facts) < facts_count:
        # split by sentences of original full text
        sents = re.split(r'(?<=[.!?])\s+', text)
        facts = [s.strip() for s in sents if s.strip()][:facts_count]
    return title, facts[:facts_count]


def call_groq(prompt, model="openai/llama3-70b-8192", temperature=0.7, max_tokens=400):
    if not GROQ_KEY:
        raise RuntimeError("GROQ_API_KEY not set")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that writes short engaging wildlife facts."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    r = requests.post(GROQ_CHAT_ENDPOINT, json=payload, headers=headers, timeout=TIMEOUT_SECS)
    r.raise_for_status()
    return r.json()


def call_gemini(prompt, model_name="gemini-1.0", temperature=0.7, max_output_tokens=1024):
    if not GEMINI_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")
    # Use google genai client if available (preferred)
    if genai:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.generate(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            prompt=prompt
        )
        # response.text or response.output[0].content[0].text
        try:
            return {"choices": [{"message": {"content": response.text}}]}
        except Exception:
            return {"choices": [{"message": {"content": str(response)}}]}
    else:
        # If google.genai not installed, attempt REST (less common)
        # NOTE: user should install google-genai for best compatibility.
        url = "https://generativelanguage.googleapis.com/v1beta2/models/%s:generateText" % model_name
        headers = {"Authorization": f"Bearer {GEMINI_KEY}", "Content-Type": "application/json"}
        payload = {"prompt": {"text": prompt}, "temperature": temperature, "maxOutputTokens": max_output_tokens}
        r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT_SECS)
        r.raise_for_status()
        data = r.json()
        # convert to openai-like structure
        text = ""
        if "candidates" in data:
            text = " ".join([c.get("output", "") for c in data.get("candidates", [])])
        elif "outputs" in data and data["outputs"]:
            text = data["outputs"][0].get("content", "")
        return {"choices": [{"message": {"content": text}}]}


def call_openai_backup(prompt, model="gpt-4o-mini", temperature=0.7, max_tokens=400):
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    if OpenAIClient is None:
        raise RuntimeError("openai package not available")
    client = OpenAIClient(api_key=OPENAI_KEY)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes short engaging wildlife facts."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    # client returns an object with .choices
    try:
        return resp.to_dict()
    except Exception:
        # resp may already be dict-like
        return resp


def generate_facts_script(animal_name, facts_count=10):
    """
    Returns:
    {
      'title': ...,
      'script': 'fact1\\nfact2\\n...',
      'description': ...,
      'tags': [...]
    }
    """
    prompt = (
        f"Write {facts_count} short engaging facts about the {animal_name} in simple English. "
        "Each fact should be 1-2 sentences, interesting and surprising where possible. "
        "Include a catchy 6-8 word title for the video at the top. "
        "At the end add a single-line call to action: 'Don't forget to subscribe and hit the bell for more!'"
    )

    # Try Groq (primary)
    errors = []
    try:
        resp = call_groq(prompt, model="openai/llama3-70b-8192")
        text = _normalize_response_text_from_openai_style(resp)
        if text:
            title, facts = _extract_title_and_facts(text, animal_name, facts_count)
            description = f"{title}\n\nFacts about the {animal_name}.\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": description, "tags": [animal_name, "wildlife", "animals"]}
    except Exception as e:
        errors.append(("groq-70b", str(e)))

    # Try Gemini (backup 1)
    try:
        resp = call_gemini(prompt, model_name="gemini-1.0", temperature=0.7)
        text = _normalize_response_text_from_openai_style(resp)
        if text:
            title, facts = _extract_title_and_facts(text, animal_name, facts_count)
            description = f"{title}\n\nFacts about the {animal_name}.\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": description, "tags": [animal_name, "wildlife", "animals"]}
    except Exception as e:
        errors.append(("gemini", str(e)))

    # Try Groq small (fast)
    try:
        resp = call_groq(prompt, model="openai/llama3-8b-8192")
        text = _normalize_response_text_from_openai_style(resp)
        if text:
            title, facts = _extract_title_and_facts(text, animal_name, facts_count)
            description = f"{title}\n\nFacts about the {animal_name}.\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": description, "tags": [animal_name, "wildlife", "animals"]}
    except Exception as e:
        errors.append(("groq-8b", str(e)))

    # Final fallback: OpenAI (if configured)
    try:
        resp = call_openai_backup(prompt, model="gpt-4o-mini")
        text = _normalize_response_text_from_openai_style(resp)
        if text:
            title, facts = _extract_title_and_facts(text, animal_name, facts_count)
            description = f"{title}\n\nFacts about the {animal_name}.\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n#animals #wildlife"
            return {"title": title, "script": "\n".join(facts), "description": description, "tags": [animal_name, "wildlife", "animals"]}
    except Exception as e:
        errors.append(("openai-backup", str(e)))

    # If all failed, raise with collected errors
    raise RuntimeError(f"All AI providers failed: {errors}")
