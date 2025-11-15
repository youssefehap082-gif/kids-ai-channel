# fetch_wikipedia.py
import argparse, time, json
from pathlib import Path
import wikipedia

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

inp = Path(args.input)
out = Path(args.output)
animals = []
if not inp.exists():
    print("Input animal_list.txt not found.")
    out.write_text(json.dumps([], indent=2, ensure_ascii=False))
    exit(0)

with inp.open(encoding='utf-8') as f:
    names = [l.strip() for l in f if l.strip()]

for n in names:
    try:
        summary = wikipedia.summary(n, sentences=3)
    except Exception:
        summary = ""
    animals.append({"name": n, "wikipedia_summary": summary})
    time.sleep(0.8)  # be gentle

out.write_text(json.dumps(animals, indent=2, ensure_ascii=False), encoding='utf-8')
print("Wrote", out)
