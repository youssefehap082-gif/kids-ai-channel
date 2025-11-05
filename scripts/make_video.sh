#!/bin/bash
mkdir -p output
# افترض أنك لديك scene1.png و scene1_cartoon.mp3
ffmpeg -loop 1 -i output/scene1.png -i output/scene1_cartoon.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -vf "scale=1280:720" output/scene1.mp4

# لو فيه أكثر من مشهد اعمل ملف mylist.txt واستخدم concat
# echo "file 'output/scene1.mp4'" > mylist.txt
# echo "file 'output/scene2.mp4'" >> mylist.txt
# ffmpeg -f concat -safe 0 -i mylist.txt -c copy output/final_episode.mp4

# لو بنعمل مشهد واحد فقط، نعيد تسميته ل final
mv output/scene1.mp4 output/final_episode.mp4
echo "Video ready: output/final_episode.mp4"
