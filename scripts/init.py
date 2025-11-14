# init.py - create data files if missing
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
DATA.mkdir(parents=True, exist_ok=True)

if not (DATA / 'used_animals.json').exists():
    (DATA / 'used_animals.json').write_text('[]')

if not (DATA / 'performance_data.json').exists():
    (DATA / 'performance_data.json').write_text('{}')

print('Initialized data folder')
