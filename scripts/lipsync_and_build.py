# scripts/lipsync_and_build.py  (FIXED & more robust)
import os
import json
import math
import subprocess
import shutil
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
import soundfile as sf

OUT = Path("output")
ASSETS = Path("assets")
OUT.mkdir(exist_ok=True)

# load script
script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json -> run generate_script.py first")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))

# load scene manifest if exists (from tts step)
manifest_path = OUT / "scene_manifest.json"
if manifest_path.exists():
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    scenes = manifest.get("scenes", [])
else:
    # fallback: look for sceneN.mp3
    scenes = []
    idx = 1
    while (OUT / f"scene{idx}.mp3").exists():
        scenes.append({"scene_index": idx, "audio": str(OUT / f"scene{idx}.mp3"), "image_prompt": ""})
        idx += 1

FPS = 25
FRAME_STEP = 1.0 / FPS

def rms_from_audio_segment(data):
    if data.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(data.astype(np.float64)))))

def ensure_png(path: Path):
    if not path.exists():
        print(f"Missing asset: {path}")
        return False
    return True

def load_image_safe(p: Path, size=None, mode="RGBA"):
    """
    Load image with fallback: if loading fails, create a simple placeholder.
    Returns an Image object in RGBA.
    """
    try:
        im = Image.open(str(p))
        # convert to RGBA safely
        if im.mode != "RGBA":
            im = im.convert("RGBA")
    except Exception as e:
        print(f"Warning: failed to open {p}: {e}. Creating placeholder.")
        # create simple placeholder
        W, H = (360, 480) if not size else size
        im = Image.new("RGBA", (W, H), (255, 230, 200, 255))
        draw = Image.new("RGBA", (W, H))
    if size:
        im = ImageOps.contain(im, size)
        # ensure exact size by padding/crop
        bg = Image.new("RGBA", size, (0,0,0,0))
        x = (size[0] - im.width) // 2
        y = (size[1] - im.height) // 2
        bg.paste(im, (x, y), im)
        im = bg
    return im

def compose_frames_for_scene(scene_idx, audio_path, bg_path, left_char, right_char, out_video_path):
    audio_path = str(audio_path)
    data, sr = sf.read(audio_path)
    duration = len(data) / sr
    print(f"Scene {scene_idx}: audio {audio_path} duration {duration:.2f}s sr={sr}")

    # prepare assets
    bg = load_image_safe(Path(bg_path), size=(1280,720))
    left_img = load_image_safe(Path(left_char), size=(360,480))
    right_img = load_image_safe(Path(right_char), size=(360,480))

    left_base = Path(left_char).stem
    right_base = Path(right_char).stem
    left_mouths = [ASSETS / f"{left_base}_mouth_closed.png", ASSETS / f"{left_base}_mouth_mid.png", ASSETS / f"{left_base}_mouth_open.png"]
    right_mouths = [ASSETS / f"{right_base}_mouth_closed.png", ASSETS / f"{right_base}_mouth_mid.png", ASSETS / f"{right_base}_mouth_open.png"]

    # fallback mouth generation if missing: small solid shapes
    def ensure_mouths(mouth_paths, base_name):
        for i,p in enumerate(mouth_paths):
            if not p.exists():
                print(f"Creating fallback mouth {p}")
                W,H = (120,60)
                im = Image.new("RGBA", (W,H), (0,0,0,0))
                d = Image.new("RGBA", (W,H), (0,0,0,0))
                if i == 0:  # closed
                    # thin rectangle
                    img = Image.new("RGBA", (W,H), (0,0,0,0))
                    from PIL import ImageDraw
                    draw = ImageDraw.Draw(img)
                    draw.rectangle((10,25,110,35), fill=(140,30,30,255))
                    img.save(p)
                elif i == 1:  # mid
                    img = Image.new("RGBA", (W,H), (0,0,0,0))
                    from PIL import ImageDraw
                    draw = ImageDraw.Draw(img)
                    draw.ellipse((5,15,115,45), fill=(140,30,30,255))
                    img.save(p)
                else:  # open
                    img = Image.new("RGBA", (W,H), (0,0,0,0))
                    from PIL import ImageDraw
                    draw = ImageDraw.Draw(img)
                    draw.ellipse((2,5,118,55), fill=(140,30,30,255))
                    img.save(p)

    ensure_mouths(left_mouths, left_base)
    ensure_mouths(right_mouths, right_base)

    frames_dir = OUT / f"frames_scene{scene_idx}"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    total_frames = max(1, int(math.ceil(duration * FPS)))
    # prepare mono audio samples
    if data.ndim > 1:
        mono = np.mean(data, axis=1)
    else:
        mono = data
    samples_per_frame = int(sr / FPS)
    for fidx in range(total_frames):
        start = fidx * samples_per_frame
        end = start + samples_per_frame
        seg = mono[start:end] if end <= len(mono) else mono[start:]
        rms = rms_from_audio_segment(seg)
        # thresholds can be tuned
        if rms < 0.005:
            mi = 0
        elif rms < 0.03:
            mi = 1
        else:
            mi = 2

        frame = bg.copy()

        # small head bob (sin wave)
        bob = int(6 * math.sin(2 * math.pi * fidx / (FPS * 2)))
        left_pos = (160, 160 + bob)
        right_pos = (760, 160 - bob)

        # paste characters
        frame.paste(left_img, left_pos, left_img)
        frame.paste(right_img, right_pos, right_img)

        # paste mouths
        try:
            left_mouth = Image.open(str(left_mouths[mi])).convert("RGBA")
            lm = left_mouth.resize((120,60))
            lm_pos = (left_pos[0] + 140, left_pos[1] + 230)
            frame.paste(lm, lm_pos, lm)
        except Exception as e:
            # ignore if mouth missing
            pass
        try:
            right_mouth = Image.open(str(right_mouths[mi])).convert("RGBA")
            rm = right_mouth.resize((120,60))
            rm_pos = (right_pos[0] + 140, right_pos[1] + 230)
            frame.paste(rm, rm_pos, rm)
        except Exception as e:
            pass

        frame_path = frames_dir / f"frame_{fidx:05d}.png"
        frame.convert("RGB").save(frame_path, "PNG")
        if (fidx % 50) == 0:
            print(f"Scene {scene_idx} frame {fidx}/{total_frames} rms={rms:.4f} mouth={mi}")

    # assemble frames into video
    tmp_video = OUT / f"scene{scene_idx}_tmp.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-r", str(FPS), "-i", str(frames_dir / "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", f"scale=1280:720", str(tmp_video)
    ], check=True)

    # merge audio
    final_scene_video = Path(out_video_path)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(tmp_video), "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final_scene_video)
    ], check=True)

    # cleanup
    try:
        shutil.rmtree(frames_dir)
    except Exception:
        pass
    try:
        tmp_video.unlink(missing_ok=True)
    except Exception:
        pass

    print("Built scene video:", final_scene_video)

# choose characters for left/right (default Max & Sam)
left_default = ASSETS / "Max.png"
right_default = ASSETS / "Sam.png"

for s in scenes:
    idx = s.get("scene_index")
    audio = s.get("audio")
    if not audio:
        print("No audio for scene", idx, "- skipping")
        continue
    bg = ASSETS / f"scene{idx}_bg.png"
    if not bg.exists():
        print("Missing background", bg, "-> skipping scene", idx)
        continue
    left = left_default if left_default.exists() else (ASSETS / "Max.png")
    right = right_default if right_default.exists() else (ASSETS / "Sam.png")
    out_scene_video = OUT / f"scene{idx}_animated.mp4"
    try:
        compose_frames_for_scene(idx, audio, bg, left, right, out_scene_video)
    except Exception as e:
        print("Error building scene", idx, ":", e)

print("Lip-sync & build completed.")
