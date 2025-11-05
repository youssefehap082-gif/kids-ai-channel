# convert text file to mp3 using gTTS (free)
from gtts import gTTS
import sys

def to_mp3(txtfile, outmp3):
    text = open(txtfile,"r",encoding="utf-8").read()
    tts = gTTS(text, lang='en')
    tts.save(outmp3)
    print("Saved", outmp3)

if __name__ == "__main__":
    to_mp3(sys.argv[1], sys.argv[2])
