# scripts/thumbnail_generator.py
"""
Thumbnail generator for YouTube videos (production-ready).

Functions:
- generate_thumbnail_for_video(video_path, title, out_path, vertical=False)
- generate_simple_thumbnail(title, out_path, vertical=False)
- _fetch_coverr_image(query)  # optional: uses COVERR_APIKEY env var
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import io
import random
import logging

logger = logging.getLogger("thumbnail_generator")
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parents[1]
TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(parents=True, exist_ok=True)

# Default sizes
SIZE_LANDSCAPE = (1280, 720)
SIZE_VERTICAL = (1080, 1920)

# Fonts: try to use a default system font; prefer "DejaVuSans-Bold"
def _load_font(size=60):
    try:
        # common on many runners
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except Exception:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=size)
        except Exception:
            return ImageFont.load_default()


def _fetch_coverr_image(query: str):
    """
    Optional fetch from Coverr (if COVERR_APIKEY provided).
    Returns PIL.Image or None.
    """
    key = os.getenv("COVERR_APIKEY") or os.getenv("COVERR_API_KEY")
    if not key:
        return None
    try:
        import requests
        url = f"https://api.coverr.co/videos?query={requests.utils.requote_uri(query)}&per_page=1"
        headers = {"Authorization": f"Bearer {key}"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        hits = data.get("data") or data.get("videos") or []
        if not hits:
            return None
        # pick thumbnail link if available
        item = hits[0]
        thumb = None
        # try common fields
        for k in ("thumbnail", "thumbnail_url", "poster"):
            if k in item:
                thumb = item[k]
                break
        if not thumb:
            # try to find preview in assets
            assets = item.get("assets") or {}
            if isinstance(assets, list) and assets:
                thumb = assets[0].get("url")
        if not thumb:
            return None
        resp = requests.get(thumb, timeout=15)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        return img
    except Exception as e:
        logger.warning("Coverr fetch failed: %s", e)
        return None


def _extract_frame_from_video(video_path: str, time_sec: float = 1.0, vertical=False):
    """
    Try to extract a representative frame using moviepy (if available).
    Returns PIL.Image or None.
    """
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(str(video_path))
        # clamp time
        t = min(max(0.5, time_sec), max(0.5, getattr(clip, "duration", 1.0) - 0.5))
        frame = clip.get_frame(t)
        clip.close()
        img = Image.fromarray(frame).convert("RGBA")
        return img
    except Exception as e:
        logger.debug("Frame extraction failed for %s: %s", video_path, e)
        return None


def _apply_gradient_overlay(base_img: Image.Image, opacity=0.6):
    """
    Apply a subtle black gradient overlay to improve text contrast.
    """
    overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    w, h = base_img.size
    for y in range(h):
        # linear gradient more dark at bottom
        a = int(255 * opacity * (y / h) * 0.9)
        line = Image.new("RGBA", (w, 1), (0, 0, 0, a))
        overlay.paste(line, (0, y))
    return Image.alpha_composite(base_img.convert("RGBA"), overlay)


def _draw_text_with_stroke(draw: ImageDraw.ImageDraw, pos, text, font, fill=(255,255,255), stroke_fill=(0,0,0), stroke_width=2):
    """
    Draw text with stroke effect for readability.
    """
    x, y = pos
    # PIL ImageDraw supports stroke_width & stroke_fill in newer versions
    try:
        draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
    except TypeError:
        # fallback manual stroke
        for ox in range(-stroke_width, stroke_width+1):
            for oy in range(-stroke_width, stroke_width+1):
                if ox == 0 and oy == 0:
                    continue
                draw.text((x+ox, y+oy), text, font=font, fill=stroke_fill)
        draw.text((x,y), text, font=font, fill=fill)


def generate_simple_thumbnail(title: str, out_path: str, vertical: bool = False, subtitle: str | None = None, watermark: str | None = None):
    """
    Generate a simple thumbnail: colored background + big title + optional subtitle and watermark.
    """
    size = SIZE_VERTICAL if vertical else SIZE_LANDSCAPE
    bg_colors = [(30,30,30), (18,90,130), (20,120,80), (90,20,40), (140,60,10)]
    bg = Image.new("RGBA", size, random.choice(bg_colors) + (255,))

    draw = ImageDraw.Draw(bg)
    font = _load_font(size=int(size[1]*0.08))  # relative size

    # title: wrap long text
    max_width = int(size[0] * 0.85)
    words = title.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        wbox = draw.textbbox((0,0), test, font=font)
        if wbox[2] > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    # center block
    total_h = sum([draw.textbbox((0,0), l, font=font)[3] for l in lines]) + (len(lines)-1)*10
    y = int((size[1] - total_h)/2)
    for ln in lines:
        wbox = draw.textbbox((0,0), ln, font=font)
        x = int((size[0] - wbox[2]) / 2)
        _draw_text_with_stroke(draw, (x, y), ln, font)
        y += wbox[3] + 10

    # subtitle
    if subtitle:
        sub_font = _load_font(size=int(size[1]*0.045))
        sub_box = draw.textbbox((0,0), subtitle, font=sub_font)
        sx = int((size[0] - sub_box[2]) / 2)
        sy = y + 10
        _draw_text_with_stroke(draw, (sx, sy), subtitle, sub_font, stroke_width=2)

    # watermark
    if watermark:
        wm_font = _load_font(size=int(size[1]*0.03))
        wbox = draw.textbbox((0,0), watermark, font=wm_font)
        draw.text((size[0]-wbox[2]-16, size[1]-wbox[3]-10), watermark, font=wm_font, fill=(255,255,255,200))

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    bg.convert("RGB").save(out, format="JPEG", quality=92)
    logger.info("Wrote simple thumbnail: %s", out)
    return out


def generate_thumbnail_for_video(video_path: str | None, title: str, out_path: str, vertical: bool = False, watermark: str | None = "@WildPlanetFacts"):
    """
    Main function: attempt frame extraction -> coverr -> simple fallback.
    Compose text on top and save thumbnail image.
    """
    size = SIZE_VERTICAL if vertical else SIZE_LANDSCAPE
    img = None

    # 1) try extract frame
    if video_path:
        img = _extract_frame_from_video(video_path, time_sec=1.5, vertical=vertical)
        if img:
            logger.info("Used frame from video for thumbnail.")

    # 2) try coverr image
    if img is None:
        q = title.split(" ")[0] if title else "animal"
        cover_img = _fetch_coverr_image(q)
        if cover_img:
            img = cover_img.resize(size, Image.LANCZOS)
            logger.info("Used Coverr image for thumbnail.")

    # 3) fallback to simple color background
    if img is None:
        logger.info("Falling back to simple thumbnail.")
        return generate_simple_thumbnail(title=title, out_path=out_path, vertical=vertical, watermark=watermark)

    # ensure size
    img = img.resize(size, Image.LANCZOS)

    # overlay gradient for contrast
    img = _apply_gradient_overlay(img, opacity=0.6)

    draw = ImageDraw.Draw(img)
    # title font large
    font = _load_font(size=int(size[1]*0.085))
    # wrap and place title (bottom-left block)
    max_w = int(size[0] * 0.85)
    words = title.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    # compute starting position (bottom-left)
    total_h = sum([draw.textbbox((0,0), l, font=font)[3] for l in lines]) + (len(lines)-1)*8
    pad = int(size[0]*0.04)
    y = size[1] - total_h - pad
    x = pad

    for ln in lines:
        _draw_text_with_stroke(draw, (x, y), ln, font, stroke_width=3)
        y += draw.textbbox((0,0), ln, font=font)[3] + 8

    # watermark
    if watermark:
        wm_font = _load_font(size=int(size[1]*0.035))
        wbox = draw.textbbox((0,0), watermark, font=wm_font)
        draw.text((size[0]-wbox[2]-16, size[1]-wbox[3]-10), watermark, font=wm_font, fill=(255,255,255,200))

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, format="JPEG", quality=92)
    logger.info("Wrote thumbnail: %s", out)
    return out


# Quick manual test
if __name__ == "__main__":
    generate_simple_thumbnail("Amazing Facts About The Lion", "data/test_thumb.jpg")
