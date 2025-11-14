import os, json, requests
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
DATA = ROOT / 'data'
ASSETS = ROOT / 'assets'
TMP = ROOT / 'tmp'
for d in (DATA, ASSETS, TMP):
    d.mkdir(parents=True, exist_ok=True)
def read_json(p): 
    if not p.exists(): return None
    return json.loads(p.read_text(encoding='utf-8'))
def write_json(p, data): 
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def download_file(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return dest
