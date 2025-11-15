import wikipedia, json, argparse
from pathlib import Path
def build_db(input_file, output_file):
    animals = [l.strip() for l in Path(input_file).read_text(encoding='utf-8').splitlines() if l.strip()]
    db = []
    for name in animals:
        try:
            s = wikipedia.summary(name, sentences=2)
        except Exception:
            s = f'Facts about {name}.'
        db.append({'name': name, 'summary': s})
    Path(output_file).write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Wrote', output_file)
if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--input', required=True); p.add_argument('--output', required=True)
    args = p.parse_args(); build_db(args.input, args.output)
