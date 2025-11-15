import os
import json
from pathlib import Path

TMP_DIR = Path("scripts/tmp")

def ensure_tmp():
    """Create temporary folder if it doesn't exist."""
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    return TMP_DIR

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_animal_database():
    db_path = Path("data/animal_database.json")
    if not db_path.exists():
        return {}
    return read_json(db_path)

def save_animal_database(data):
    db_path = Path("data/animal_database.json")
    write_json(db_path, data)
