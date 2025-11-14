# scripts/tools/TextClip.py
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip

class TextClip(ImageClip):
    def __init__(self, txt, fontsize=40, color='white', bg_color='black', size=None, font='Arial'):
        if size is None:
            size = (1280, 720)

        img = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(font, fontsize)
        except:
            font = ImageFont.load_default()

        w, h = draw.textsize(txt, font=font)
        draw.text(((size[0]-w)//2, (size[1]-h)//2), txt, font=font, fill=color)

        arr = np.array(img)
        super().__init__(arr)
