# scripts/whiteboard_anim.py
import os, math, subprocess, textwrap, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

OUT = Path("output")
ASSETS = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

script = json.load(open(OUT/"script.json", encoding="utf-8"))
scenes = script.get("scenes", [])

FRAMERATE = 24

def get_audio_duration(path):
    try:
        out = subprocess.check_output([
            "ffprobe","-v","error","-show_entries","format=duration",
            "-of","default=noprint_wrappers=1:nokey=1", str(path)
        ])
        return float(out.strip())
    except Exception:
        return None

def make_scene_frames(idx, scene):
    sketch_path = ASSETS / f"scene{idx}_sketch.png"
    if not sketch_path.exists():
        print("Missing sketch", sketch_path, "-> skipping")
        return None
    audio_path = OUT / f"scene{idx}.mp3"
    dur = get_audio_duration(audio_path) if audio_path.exists() else None
    if dur is None:
        dur = max(60.0, min(120.0, len(scene.get("text",""))/5.0 + 40.0))  # aim 60-120s per scene
    print(f"Scene {idx} duration {dur:.1f}s")

    # font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 54)
    except:
        font = ImageFont.load_default()
        font_h = font

    wb_text = scene.get("whiteboard_text", scene.get("text",""))
    total_chars = len(wb_text)
    total_frames = int(math.ceil(dur * FRAMERATE))
    frames_dir = OUT / f"frames_scene{idx}"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    # load sketch and resize
    sketch = Image.open(sketch_path).convert("RGBA")
    sk_w = 520
    scale = sk_w / sketch.width
    sk_h = int(sketch.height * scale)
    sketch = sketch.resize((sk_w, sk_h), Image.LANCZOS)

    # char reveal: distribute characters across frames
    for f in range(total_frames):
        chars_to_show = int((f / (total_frames - 1)) * total_chars) if total_frames>1 else total_chars
        text_shown = wb_text[:chars_to_show]
        img = Image.new("RGB", (1280,720), (255,255,255))
        draw = ImageDraw.Draw(img)
        # paste sketch right
        x_sk = 1280 - sk_w - 60
        y_sk = (720 - sk_h)//2
        img.paste(sketch, (x_sk, y_sk), sketch)
        # draw headline top-left
        left_margin = 60
        draw.text((left_margin, 20), scene.get("headline",""), fill=(0,0,0), font=font_h)
        # write text lines
        lines = []
        for p in text_shown.split("\n"):
            wrapped = textwrap.wrap(p, width=30)
            if not wrapped:
                lines.append("")
            else:
                lines.extend(wrapped)
        y = 110
        for line in lines:
            draw.text((left_margin, y), line, fill=(0,0,0), font=font)
            y += font.getsize(line)[1] + 8
        # optionally overlay a hand image if exists for effect
        hand_path = ASSETS / "hand.png"
        if hand_path.exists():
            try:
                hand = Image.open(hand_path).convert("RGBA")
                # position the hand near the latest text (approx bottom-left)
                hw = int(200)
                hh = int(hand.height * (hw / hand.width))
                hand = hand.resize((hw, hh), Image.LANCZOS)
                img.paste(hand, (left_margin + 200, min(y, 520)), hand)
            except Exception:
                pass
        frame_path = frames_dir / f"frame_{f:05d}.png"
        img.save(frame_path)
    # render to video
    tmp = OUT / f"scene{idx}_tmp.mp4"
    cmd = [
        "ffmpeg","-y","-r", str(FRAMERATE), "-i", str(frames_dir / "frame_%05d.png"),
        "-c:v","libx264","-pix_fmt","yuv420p", str(tmp)
    ]
    print("Rendering frames to:", tmp)
    subprocess.run(cmd, check=True)
    # attach audio
    final_scene = OUT / f"scene{idx}_final.mp4"
    if audio_path.exists():
        subprocess.run([
            "ffmpeg","-y","-i", str(tmp), "-i", str(audio_path),
            "-c:v","copy","-c:a","aac","-b:a","192k", str(final_scene)
        ], check=True)
    else:
        shutil.move(str(tmp), str(final_scene))
    # cleanup
    shutil.rmtree(frames_dir)
    try:
        tmp.unlink(missing_ok=True)
    except:
        pass
    return final_scene

scene_files = []
for s in scenes:
    idx = s.get("idx")
    print("Building scene", idx)
    try:
        out = make_scene_frames(idx, s)
        if out:
            scene_files.append(out)
    except Exception as e:
        print("Error building scene", idx, e)

if not scene_files:
    print("No scenes created. Exiting.")
    raise SystemExit(1)

# concat
list_file = OUT / "mylist.txt"
with open(list_file, "w", encoding="utf-8") as f:
    for p in scene_files:
        f.write(f"file '{p.name}'\n")

cwd = os.getcwd()
os.chdir(str(OUT))
try:
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i","mylist.txt","-c","copy","final_episode.mp4"], check=True)
    # make short <= 120s
    subprocess.run(["ffmpeg","-y","-i","final_episode.mp4","-ss","0","-t","120","-c","copy","short_episode.mp4"], check=True)
    print("Built final_episode.mp4 and short_episode.mp4")
finally:
    os.chdir(cwd)
