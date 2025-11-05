#!/bin/bash
set -euo pipefail
OUTDIR="output"
MANIFEST="$OUTDIR/scene_manifest.json"
if [ ! -f "$MANIFEST" ]; then echo "No manifest"; exit 1; fi
rm -f "$OUTDIR"/scene*.mp4 mylist.txt "$OUTDIR/_scene_list.txt" || true
python3 scripts/emit_scene_list.py > "$OUTDIR/_scene_list.txt"
i=0
while IFS=$'\t' read -r idx audio prompt; do
  [ -z "$idx" ] && continue
  img="$OUTDIR/scene${idx}.png"
  if [ ! -f "$img" ]; then
    echo "Generating image for scene $idx"
    python3 scripts/generate_image.py "$prompt" "$img" || true
  fi
  if [ ! -f "$audio" ]; then
    echo "Audio $audio missing, creating silent fallback"
    ffmpeg -y -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 1 -q:a 9 -acodec libmp3lame "$OUTDIR/scene${idx}_silent.mp3"
    audio="$OUTDIR/scene${idx}_silent.mp3"
  fi
  # print audio duration
  dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$audio" || echo 0)
  echo "Scene $idx: audio=$audio duration=${dur}s image=$img"
  mp4="$OUTDIR/scene${idx}.mp4"
  ffmpeg -y -loop 1 -i "$img" -i "$audio" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -vf "scale=1280:720" "$mp4"
  printf "file '%s'\n" "$mp4" >> mylist.txt
  i=$((i+1))
done < "$OUTDIR/_scene_list.txt"
if [ $i -eq 0 ]; then echo "No scenes"; exit 1; fi
echo "Concatenating $i scenes..."
ffmpeg -y -f concat -safe 0 -i mylist.txt -c copy "$OUTDIR/final_episode.mp4"
echo "Final at $OUTDIR/final_episode.mp4"
