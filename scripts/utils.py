# scripts/utils.py
import os
import requests
from pathlib import Path
import logging

log = logging.getLogger("utils")

def safe_mkdir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def download_file(url, dest: Path, timeout=30):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, stream=True, timeout=timeout)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(1024*32):
            if chunk:
                f.write(chunk)
    return dest

def read_json(path):
    import json
    return json.loads(Path(path).read_text())

def write_text(path, text):
    Path(path).write_text(text, encoding="utf-8")
