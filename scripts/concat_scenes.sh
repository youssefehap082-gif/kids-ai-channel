#!/bin/bash
set -euo pipefail

OUTDIR="output"
LIST="$OUTDIR/mylist.txt"
FINAL="$OUTDIR/final_episode.mp4"

# cleanup previous list/final
rm -f "$LIST" "$FINAL" || true

# go into OUTDIR to make file paths relative to list
pushd "$OUTDIR" >/dev/null

# create list of animated scene files using basename only
shopt -s nullglob
found=0
for f in scene*_animated.mp4; do
  echo "file '$f'" >> "$LIST"
  found=1
done
shopt -u nullglob

if [ $found -eq 0 ]; then
  echo "No animated scene files found in $OUTDIR (pattern scene*_animated.mp4)."
  popd >/dev/null
  exit 1
fi

echo "Contents of $LIST:"
cat "$LIST"

# run ffmpeg concat from inside OUTDIR (paths inside list are relative to here)
ffmpeg -y -f concat -safe 0 -i "$LIST" -c copy "$FINAL"

popd >/dev/null

echo "Final episode at $OUTDIR/$(basename "$FINAL")"
