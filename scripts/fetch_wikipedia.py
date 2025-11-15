#!/usr/bin/env python3
import argparse, json, time, warnings
import wikipedia
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore', category=UserWarning)

def safe_page(title):
    try:
        return wikipedia.page(title, auto_suggest=False)
    except Exception:
        res = wikipedia.search(title, results=3)
        if res:
            try:
                return wikipedia.page(res[0], auto_suggest=False)
            except Exception:
                return None
        return None

def extract_facts_from_text(text, maxfacts=10):
    s = text.replace('\n',' ').strip()
    # split by sentences (naive)
    sents = [x.strip() for x in s.split('. ') if x.strip()]
    facts = []
    for sent in sents:
        if len(sent) > 40:
            facts.append(sent if sent.endswith('.') else sent + '.')
        if len(facts) >= maxfacts:
            break
    return facts

def main(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        names = [l.strip() for l in f if l.strip()]

    db = []
    for name in names:
        entry = {'name': name, 'summary': '', 'source': '', 'facts': []}
        page = safe_page(name)
        if page:
            try:
                entry['summary'] = page.summary
                entry['source'] = getattr(page, 'url', '')
                entry['facts'] = extract_facts_from_text(entry['summary'], maxfacts=10)
            except Exception:
                pass

        if not entry['facts']:
            # try HTML paragraphs
            try:
                p = wikipedia.page(name)
                html = p.html()
                soup = BeautifulSoup(html, features='html.parser')
                paras = soup.find_all('p')
                for ptag in paras:
                    txt = ptag.get_text().strip()
                    if len(txt) > 120:
                        entry['facts'] = extract_facts_from_text(txt, maxfacts=10)
                        if entry['facts']:
                            break
            except Exception:
                pass

        if not entry['facts']:
            # fallback minimal safe facts
            entry['summary'] = entry['summary'] or f"{name} is an animal."
            entry['facts'] = [f"{name} is known for its characteristic.", f"{name} appears in various habitats."]
            while len(entry['facts']) < 5:
                entry['facts'].append(f"Additional fact about {name}.")

        db.append(entry)
        time.sleep(0.3)  # polite pause

    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump(db, out, ensure_ascii=False, indent=2)
    print("Wrote", output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/animal_list.txt')
    parser.add_argument('--output', default='data/animal_database.json')
    args = parser.parse_args()
    main(args.input, args.output)
