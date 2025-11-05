#!/bin/bash
set -euo pipefail

OUTDIR="output"
mkdir -p "$OUTDIR"

MANIFEST="$OUTDIR/scene_manifest.json"
if [ ! -f "$MANIFEST" ]; then
  echo "Error: $MANIFEST not found. Run tts_openai.py first."
  exit 1
fi

# cleanup previous outputs
rm -f "$OUTDIR"/scene*.mp4 mylist.txt || true

# Read manifest (simple jq-less parsing by Python)
python3 - <<'PY'
import json, sys
m = json.load(open("output/scene_manifest.json",encoding="utf-8"))
for s in m["scenes"]:
    print(s["scene_index"], s["audio"], s["image_prompt"])
PY > output/_scene_list.txt

i=0
while read -r idx audio prompt_line; do
  if [ -z "$idx" ]; then
    continue
  fi
  scene_idx="$idx"
  audio_file="$audio"
  img_file="$OUTDIR/scene${scene_idx}.png"

  # generate image for scene if not exists
  if [ ! -f "$img_file" ]; then
    echo "Generating image for scene $scene_idx"
    python3 scripts/generate_image.py "$prompt_line" "$img_file" || true
  fi

  # build video from image+audio
  scene_mp4="$OUTDIR/scene${scene_idx}.mp4"
  echo "Building scene video $scene_mp4"
  ffmpeg -y -loop 1 -i "$img_file" -i "$audio_file" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -vf "scale=1280:720" "$scene_mp4"

  printf "file '%s'\n" "$scene_mp4" >> mylist.txt
  i=$((i+1))
done < output/_scene_list.txt

if [ $i -eq 0 ]; then
  echo "No scenes created."
  exit 1
fi

echo "Concatenating $i scenes..."
ffmpeg -y -f concat -safe 0 -i mylist.txt -c copy "$OUTDIR/final_episode.mp4"
echo "Final episode at $OUTDIR/final_episode.mp4"
