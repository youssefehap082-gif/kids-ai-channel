#!/bin/bash
set -euo pipefail

# scripts/make_video.sh
# - يبحث عن ملفات mp3 في output/*.mp3 (مثال: output/scene1.mp3)
# - يحوّل كل ملف لصوت "كرتوني" بنفس الطبقة لكن بدون تسريع
# - يولّد فيديو لكل مشهد من صورة مقابلة (output/scene1.png)
# - يدمج المشاهد في ملف واحد output/final_episode.mp4

OUTDIR="output"
mkdir -p "$OUTDIR"

# إعدادات الصوت الكرتوني (تقدر تغيّر pitch_multiplier إذا حبيت)
PITCH_MULTIPLIER=1.15
# atempo must be ~ 1 / PITCH_MULTIPLIER
ATEMPO=$(awk "BEGIN{printf \"%.4f\", 1/${PITCH_MULTIPLIER}}")

echo "Using pitch multiplier=${PITCH_MULTIPLIER}, atempo=${ATEMPO}"

# نظف أي ملفات قديمة
rm -f "$OUTDIR"/*.mp4 "$OUTDIR"/*_cartoon.mp3 mylist.txt || true

shopt -s nullglob
MP3_FILES=("$OUTDIR"/*.mp3)

if [ ${#MP3_FILES[@]} -eq 0 ]; then
  echo "No mp3 files found in $OUTDIR. Expecting files like output/scene1.mp3"
  exit 1
fi

i=0
for mp3 in "${MP3_FILES[@]}"; do
  basename=$(basename "$mp3" .mp3)   # e.g., scene1
  cartoon_mp3="$OUTDIR/${basename}_cartoon.mp3"
  img="$OUTDIR/${basename}.png"
  scene_mp4="$OUTDIR/${basename}.mp4"

  echo "Processing $mp3 -> $cartoon_mp3"

  # 1) make cartoon voice (pitch up but keep same duration)
  ffmpeg -y -i "$mp3" -af "asetrate=44100*${PITCH_MULTIPLIER},aresample=44100,atempo=${ATEMPO},volume=1.05,loudnorm" "$cartoon_mp3"

  # 2) ensure we have an image for this scene; if not, create a simple color placeholder
  if [ ! -f "$img" ]; then
    echo "Image $img not found — creating placeholder."
    ffmpeg -y -f lavfi -i color=c=lightblue:s=1280x720 -frames:v 1 "$img"
  fi

  # 3) build scene video (image + cartoon audio)
  echo "Building video for $basename"
  ffmpeg -y -loop 1 -i "$img" -i "$cartoon_mp3" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -vf "scale=1280:720" "$scene_mp4"

  # add to concat list
  printf "file '%s'\n" "$scene_mp4" >> mylist.txt
  i=$((i+1))
done

if [ $i -eq 0 ]; then
  echo "No scenes produced."
  exit 1
fi

# 4) concat into final file
echo "Concatenating $i scenes..."
ffmpeg -y -f concat -safe 0 -i mylist.txt -c copy "$OUTDIR/final_episode.mp4"

echo "Final video: $OUTDIR/final_episode.mp4"
