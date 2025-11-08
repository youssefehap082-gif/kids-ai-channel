import json, os, random
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STATE_FILE = DATA / "state.json"

def load_state() -> Dict:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps({"done_animals": [], "last_run_utc": None}, indent=2))
    return json.loads(STATE_FILE.read_text())

def save_state(state: Dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def pick_unique_animals(pool: List[str], n: int=3) -> List[str]:
    st = load_state()
    done = set(map(str.lower, st.get("done_animals", [])))
    candidates = [a for a in pool if a.lower() not in done]
    if len(candidates) < n:
        done = set()
        candidates = pool[:]
        st["done_animals"] = []
    choice = random.sample(candidates, n)
    st["done_animals"] = st.get("done_animals", []) + choice
    st["last_run_utc"] = datetime.now(timezone.utc).isoformat()
    save_state(st)
    return choice

def slugify(name: str) -> str:
    return "".join(c for c in name.lower() if c.isalnum() or c in "-_ ").strip().replace(" ", "-")

def chunk_text(lines, max_chars=240):
    out, cur = [], ""
    for ln in lines:
        if len(cur) + len(ln) + 1 <= max_chars:
            cur += (("\n" if cur else "") + ln)
        else:
            out.append(cur)
            cur = ln
    if cur: out.append(cur)
    return out
