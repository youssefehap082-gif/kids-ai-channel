"""
scripts/error_recovery.py
System-wide Auto Patch & Recovery Engine (config-patching).
On failure, attempt to change config defaults (e.g., switch provider order).
This is intentionally conservative: it writes to config files only when safe.
"""
import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("kids_ai.recovery")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "providers_priority.json")

def recover_from_exception(exc: Exception, context: Dict[str,Any]=None):
    logger.warning("Recovery triggered for exception: %s", exc)
    context = context or {}
    # conservative strategy: if provider failure, rotate priority by moving first to end
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        logger.error("Cannot load providers config during recovery: %s", e)
        return False
    # detect common keys
    if "text" in cfg and isinstance(cfg["text"], list) and len(cfg["text"]) > 1:
        old = cfg["text"].copy()
        cfg["text"] = old[1:] + old[:1]
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            logger.info("Rotated text providers order for recovery: %s -> %s", old, cfg["text"])
            return True
        except Exception as e:
            logger.error("Failed to write providers config: %s", e)
            return False
    return False
