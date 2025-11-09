import tempfile
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip

def _measure(draw, text, font):
    if hasattr(draw, "textbbox"):
        l,t,r,b = draw.textbbox((0,0), text, font=font); return r-l, b-t
    return draw.textsize(text, font=font)

def _render_text_image(text: str, width=1280, pad=24):
    W = width
    # dynamic height box
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()

    # wrap long lines roughly
    words = text.split()
    lines=[]; line=""
    for w in words:
        test = (line+" "+w).strip()
        img = Image.new("RGBA",(W,10),(0,0,0,0))
        d = ImageDraw.Draw(img)
        tw,th = _measure(d,test,font)
        if tw > W - 2*pad and line:
            lines.append(line)
            line = w
        else:
            line = test
    if line: lines.append(line)

    # compute final height
    img = Image.new("RGBA",(W,10),(0,0,0,0))
    d = ImageDraw.Draw(img)
    total_h = 0
    sizes=[]
    for ln in lines:
        tw,th = _measure(d, ln, font)
        sizes.append((tw,th))
        total_h += th + 10
    total_h += pad*2

    box = Image.new("RGBA",(W,total_h),(0,0,0,0))
    d = ImageDraw.Draw(box)
    # semi-transparent black background
    d.rectangle([(0,0),(W,total_h)], fill=(0,0,0,140))
    y = pad
    for i,ln in enumerate(lines):
        tw,th = sizes[i]
        d.text(((W - tw)//2, y), ln, font=font, fill=(255,255,255,255))
        y += th + 10

    path = tempfile.mktemp(suffix=".png")
    box.save(path)
    return path, total_h

def add_subtitles(video_path: str, narration_text: str, seconds_per_sentence: float = 3.0) -> str:
    base = VideoFileClip(video_path)
    sentences = [s.strip() for s in narration_text.replace("\n"," ").split(".") if s.strip()]
    overlays=[]
    t = 0.0
    for s in sentences:
        img_path, _ = _render_text_image(s, width=base.w)
        clip = (ImageClip(img_path)
                .set_duration(seconds_per_sentence)
                .set_start(t)
                .set_position(("center","bottom"))
                .margin(bottom=60, opacity=0))
        overlays.append(clip)
        t += seconds_per_sentence
        if t >= base.duration: break

    final = CompositeVideoClip([base, *overlays])
    out = tempfile.mktemp(suffix="_sub.mp4")
    final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac")
    base.close()
    for c in overlays: c.close()
    return out
