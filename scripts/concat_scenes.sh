#!/bin/bash
set -euo pipefail

OUTDIR="output"
LIST_BASENAME="mylist.txt"
FINAL="final_episode.mp4"

# cleanup previous list/final (in OUTDIR)
rm -f "$OUTDIR/$LIST_BASENAME" "$OUTDIR/$FINAL" || true

# go into OUTDIR to make file paths relative to list
pushd "$OUTDIR" >/dev/null

# create list of animated scene files using basename only
shopt -s nullglob
found=0
for f in scene*_animated.mp4; do
  echo "file '$f'" >> "$LIST_BASENAME"
  found=1
done
shopt -u nullglob

if [ $found -eq 0 ]; then
  echo "No animated scene files found in $OUTDIR (pattern scene*_animated.mp4)."
  popd >/dev/null
  exit 1
fi

echo "Contents of $OUTDIR/$LIST_BASENAME:"
cat "$LIST_BASENAME"

# run ffmpeg concat from inside OUTDIR (paths inside list are relative to here)
ffmpeg -y -f concat -safe 0 -i "$LIST_BASENAME" -c copy "$FINAL"

popd >/dev/null

echo "Final episode at $OUTDIR/$FINAL"
