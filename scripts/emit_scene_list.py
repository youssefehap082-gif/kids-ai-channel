#!/usr/bin/env python3
import json,sys
m=json.load(open("output/scene_manifest.json",encoding="utf-8"))
for s in m.get("scenes",[]):
    print(f"{s.get('scene_index')}\t{s.get('audio')}\t{s.get('image_prompt','')}")
