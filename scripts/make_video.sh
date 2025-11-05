#!/bin/bash
set -euo pipefail

# scripts/make_video.sh (fixed - no here-doc)
OUTDIR="output"
mkdir -p "$OUTDIR"

MANIFEST="$OUTDIR/scene_manifest.json"
if [ ! -f "$MANIFEST" ]; then
  echo "Error: $MANIFEST not found. Run tts_openai.py first."
  exit 1
fi

# cleanup previous outputs
rm -f "$OUTDIR"/scene*.mp4 mylist.txt "$OUTDIR/_scene_list.txt" || true

# Produce a simple scene list (tab-separated) using the helper python script
python3 scripts/emit_scene_list.py > "$OUTDIR/_scene_list.txt"

i=0
while IFS=$'\t' read -r idx audio prompt_line; do
  if [ -z "$idx" ]; then
    continue
  fi

  scene_idx="$idx"
  audio_file="$audio"
  img_file="$OUTDIR/scene${scene_idx}.png"
  scene_mp4="$OUTDIR/scene${scene_idx}.mp4"

  # generate image for scene if not exists
  if [ ! -f "$img_file" ]; then
    echo "Generating image for scene $scene_idx"
    python3 scripts/generate_image.py "$prompt_line" "$img_file" || true
  fi

  # verify audio exists
  if [ ! -f "$audio_file" ]; then
    echo "Warning: audio file $audio_file for scene $scene_idx not found. Creating 1s silence fallback."
    ffmpeg -y -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 1 -q:a 9 -acodec libmp3lame "$OUTDIR/scene${scene_idx}_silent.mp3"
    audio_file="$OUTDIR/scene${scene_idx}_silent.mp3"
  fi

  echo "Building video for scene $scene_idx -> $scene_mp4"
  ffmpeg -y -loop 1 -i "$img_file" -i "$audio_file" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -vf "scale=1280:720" "$scene_mp4"

  printf "file '%s'\n" "$scene_mp4" >> mylist.txt
  i=$((i+1))
done < "$OUTDIR/_scene_list.txt"

if [ $i -eq 0 ]; then
  echo "No scenes created."
  exit 1
fi

echo "Concatenating $i scenes..."
ffmpeg -y -f concat -safe 0 -i mylist.txt -c copy "$OUTDIR/final_episode.mp4"
echo "Final episode at $OUTDIR/final_episode.mp4"
