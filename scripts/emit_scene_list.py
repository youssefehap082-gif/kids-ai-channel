#!/usr/bin/env python3
# scripts/emit_scene_list.py
# يقرأ output/scene_manifest.json ويطبع سطور بتنسيق:
# scene_index<TAB>audio_path<TAB>image_prompt

import json
import sys
from pathlib import Path

manifest_path = Path("output/scene_manifest.json")
if not manifest_path.exists():
    print("Error: scene_manifest.json not found", file=sys.stderr)
    sys.exit(1)

data = json.loads(manifest_path.read_text(encoding="utf-8"))
scenes = data.get("scenes", [])
for s in scenes:
    idx = s.get("scene_index", "")
    audio = s.get("audio", "").replace("\n"," ").replace("\t"," ")
    prompt = s.get("image_prompt", "").replace("\n"," ").replace("\t"," ")
    # print tab-separated (safe for shell read)
    print(f"{idx}\t{audio}\t{prompt}")
