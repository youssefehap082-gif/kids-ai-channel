#!/usr/bin/env python3
import requests
from pathlib import Path
HEADERS = {'User-Agent': 'YT-Automation/1.0'}

def download_file(url, dest: Path, timeout=60):
    r = requests.get(url, stream=True, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return dest
