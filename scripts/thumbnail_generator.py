from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
def make_thumbnail(base_image_path, title_text, out_path):
    im = Image.open(base_image_path).convert('RGB')
    im = im.resize((1280,720))
    draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 60)
    except:
        font = ImageFont.load_default()
    overlay = Image.new('RGBA', im.size, (0,0,0,80))
    im = Image.alpha_composite(im.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(im)
    lines = []
    words = title_text.split()
    line = ''
    for w in words:
        if len(line + ' ' + w) > 28:
            lines.append(line.strip()); line = w
        else:
            line = (line + ' ' + w).strip()
    if line: lines.append(line)
    y = 160
    for l in lines[:3]:
        draw.text((60,y), l, font=font, fill=(255,255,255))
        y += 80
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.convert('RGB').save(out, format='JPEG', quality=90)
    return out
