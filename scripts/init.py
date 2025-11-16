# scripts/init.py
from pathlib import Path
import json

DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)
if not (DATA / "used_animals.json").exists():
    (DATA / "used_animals.json").write_text("[]")
if not (DATA / "performance_data.json").exists():
    (DATA / "performance_data.json").write_text("{}")
if not (DATA / "animal_database.json").exists():
    # empty placeholder; will be generated on first run
    (DATA / "animal_database.json").write_text("{}")
