from pathlib import Path
import csv

def load_animals_pool(csv_path: Path):
    pool = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            pool.append(row["name"].strip())
    return pool
