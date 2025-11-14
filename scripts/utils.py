# utils.py - helpers
import os, json, requests
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
DATA = ROOT / 'data'
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

def download_file(url, dest: Path):
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in resp.iter_content(1024*32):
            f.write(chunk)
    return dest

def read_json(path):
    return json.loads(open(path).read())

def write_json(path, data):
    open(path, 'w').write(json.dumps(data, indent=2))
