# scripts/fetch_wikipedia.py
"""
Simple Wikipedia fetcher with safety:
- uses wikipedia package
- returns cleaned sentences
- handles disambiguation and timeouts
"""
import wikipedia
import logging
import re
from pathlib import Path

log = logging.getLogger("fetch_wikipedia")
wikipedia.set_lang("en")


def clean_text(t: str) -> str:
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def fetch_summary_sentences(name: str, max_sentences: int = 8):
    try:
        page = wikipedia.page(name, auto_suggest=True, redirect=True)
        summary = page.summary
    except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
        log.warning("Wiki fallback for %s: %s", name, e)
        try:
            summary = wikipedia.summary(name, sentences=5, auto_suggest=False)
        except Exception as ee:
            log.error("Wikipedia second fallback failed: %s", ee)
            return []
    except Exception as e:
        log.error("Wikipedia fetch error: %s", e)
        return []

    # split into sentences
    sents = [clean_text(s) for s in summary.split('. ') if len(s.strip()) > 30]
    return sents[:max_sentences]
