#!/bin/bash
set -euo pipefail
OUTDIR="output"
rm -f "$OUTDIR/mylist.txt" "$OUTDIR/final_episode.mp4" || true
for f in "$OUTDIR"/scene*_animated.mp4; do
  [ -f "$f" ] || continue
  echo "file '$f'" >> "$OUTDIR/mylist.txt"
done
if [ ! -f "$OUTDIR/mylist.txt" ]; then
  echo "No animated scenes found."
  exit 1
fi
ffmpeg -y -f concat -safe 0 -i "$OUTDIR/mylist.txt" -c copy "$OUTDIR/final_episode.mp4"
echo "Final episode at $OUTDIR/final_episode.mp4"
