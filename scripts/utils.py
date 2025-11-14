# utils.py - helpers for API calls, downloading assets, small utilities
import os
import requests
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
DATA = ROOT / 'data'
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

HEADERS = {'User-Agent': 'YT-Automation/1.0'}

def download_file(url, dest: Path):
    resp = requests.get(url, stream=True, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in resp.iter_content(1024 * 32):
            f.write(chunk)
    return dest

def read_json(path):
    return json.loads(open(path).read())

def write_json(path, data):
    open(path, 'w').write(json.dumps(data, indent=2))
