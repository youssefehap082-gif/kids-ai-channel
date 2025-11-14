#!/usr/bin/env python3
"""Fetch basic facts from Wikipedia for each species in an input list and create a structured JSON database.

Usage: python3 fetch_wikipedia.py --input data/animal_list.txt --output data/animal_database.json
"""
import argparse, json, time, sys, os
import wikipedia

def safe_search(title):
    try:
        res = wikipedia.search(title, results=3)
        if not res:
            return None
        # prefer exact match
        if title in res:
            return title
        return res[0]
    except Exception as e:
        return None

def fetch_summary(title):
    try:
        page = wikipedia.page(title, auto_suggest=False)
        summary = page.summary
        return summary, page.url
    except Exception:
        try:
            # try search then page
            s = safe_search(title)
            if not s:
                return None, None
            page = wikipedia.page(s, auto_suggest=False)
            return page.summary, page.url
        except Exception:
            return None, None

def main(inp, outp):
    with open(inp, 'r', encoding='utf-8') as f:
        items = [l.strip() for l in f if l.strip()]
    db = []
    for name in items:
        summary, url = fetch_summary(name)
        entry = {
            'name': name,
            'summary': summary or '',
            'source': url or '',
            'facts': []
        }
        # simple heuristics: split summary into sentences as facts
        if summary:
            sents = [s.strip() for s in summary.split('. ') if s.strip()]
            entry['facts'] = sents[:10]
        db.append(entry)
        time.sleep(0.5)
    with open(outp, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    main(args.input, args.output)
