# scripts/lipsync_and_build.py
import os, json, math, subprocess
from pathlib import Path
from PIL import Image
import numpy as np
import soundfile as sf

OUT = Path("output")
ASSETS = Path("assets")
OUT.mkdir(exist_ok=True)

script = json.load(open(OUT/"script.json", encoding="utf-8"))
manifest = json.load(open(OUT/"scene_manifest.json", encoding="utf-8")) if (OUT/"scene_manifest.json").exists() else None

# load scene manifest created by tts step if exists; otherwise create from audio files
scenes = []
if manifest:
    scenes = manifest["scenes"]
else:
    # simple creation: look for sceneN.mp3 files
    idx = 1
    while (OUT/f"scene{idx}.mp3").exists():
        scenes.append({"scene_index": idx, "audio": str(OUT/f"scene{idx}.mp3"), "image_prompt": ""})
        idx += 1

FPS = 25
FRAME_STEP = 1.0 / FPS

def rms_from_audio_segment(data):
    if data.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(data.astype(np.float64)))))

def ensure_png(p:Path):
    if not p.exists():
        print("Missing asset:", p)
        return False
    return True

def compose_frames_for_scene(scene_idx, audio_path, bg_path, left_char, right_char, out_video_path):
    # load audio to get duration
    data, sr = sf.read(audio_path)
    duration = len(data) / sr
    print(f"Scene {scene_idx}: audio {audio_path} duration {duration:.2f}s sr={sr}")
    # load assets
    bg = Image.open(bg_path).convert("RGBA").resize((1280,720))
    left_img = Image.open(left_char).convert("RGBA').resize((360,480)")
    right_img = Image.open(right_char).convert("RGBA').resize((360,480)")
    # mouth assets (assume left/right names exist)
    left_base = left_char.stem
    right_base = right_char.stem
    left_mouths = [ASSETS/f"{left_base}_mouth_closed.png", ASSETS/f"{left_base}_mouth_mid.png", ASSETS/f"{left_base}_mouth_open.png"]
    right_mouths = [ASSETS/f"{right_base}_mouth_closed.png", ASSETS/f"{right_base}_mouth_mid.png", ASSETS/f"{right_base}_mouth_open.png"]
    for m in left_mouths+right_mouths:
        if not m.exists():
            print("Warning: missing mouth asset", m)

    # create frames folder
    frames_dir = OUT/f"frames_scene{scene_idx}"
    if frames_dir.exists():
        # cleanup old
        for f in frames_dir.iterdir():
            f.unlink()
    else:
        frames_dir.mkdir(parents=True)

    total_frames = max(1, int(math.ceil(duration * FPS)))
    # read audio samples per frame (mono)
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
        # map rms to mouth index: thresholds empirical
        if rms < 0.01:
            mi = 0
        elif rms < 0.05:
            mi = 1
        else:
            mi = 2
        # create frame by compositing
        frame = bg.copy()
        # calculate positions for characters
        left_pos = (160, 160)   # tune if needed
        right_pos = (760, 160)
        frame.paste(left_img, left_pos, left_img)
        frame.paste(right_img, right_pos, right_img)
        # overlay mouth for speaking character(s)
        # simple heuristic: who is speaking? We'll check audio energy; for simplicity we'll animate both mouths based on rms
        # left mouth
        try:
            left_mouth = Image.open(left_mouths[mi]).convert("RGBA").resize((120,60))
            # mouth position relative to left head (tune)
            lm_pos = (left_pos[0]+140, left_pos[1]+230)
            frame.paste(left_mouth, lm_pos, left_mouth)
        except Exception as e:
            pass
        try:
            right_mouth = Image.open(right_mouths[mi]).convert("RGBA").resize((120,60))
            rm_pos = (right_pos[0]+140, right_pos[1]+230)
            frame.paste(right_mouth, rm_pos, right_mouth)
        except Exception as e:
            pass

        # small head bob: translate characters up/down by sin wave
        bob = int(4 * math.sin(2*math.pi * fidx / (FPS*2)))
        # note: we didn't apply bob above, for simplicity we can ignore or implement by shifting positions.

        frame_path = frames_dir / f"frame_{fidx:05d}.png"
        frame.convert("RGB").save(frame_path, "PNG")
        if fidx % 50 == 0:
            print(f"Scene {scene_idx} frame {fidx}/{total_frames} rms={rms:.4f} mouth={mi}")

    # assemble frames into video and merge audio
    tmp_video = OUT/f"scene{scene_idx}_tmp.mp4"
    # ffmpeg -r FPS -i frames/frame_%05d.png -c:v libx264 -pix_fmt yuv420p -r FPS tmp_video
    subprocess.run(["ffmpeg","-y","-r", str(FPS), "-i", str(frames_dir/"frame_%05d.png"),
                    "-c:v","libx264","-pix_fmt","yuv420p","-vf", f"scale=1280:720", str(tmp_video)], check=True)
    # merge audio
    subprocess.run(["ffmpeg","-y","-i", str(tmp_video), "-i", audio_path, "-c:v","copy","-c:a","aac","-b:a","192k", str(out_video_path)], check=True)
    # cleanup frames_dir and tmp video
    for p in frames_dir.iterdir():
        p.unlink()
    frames_dir.rmdir()
    tmp_video.unlink(missing_ok=True)
    print("Built scene video:", out_video_path)

# Plan for mapping: we'll pair characters left/right per scene by simple rule:
# left=Max, right=Sam, else if other characters present we default to left or right
for s in scenes:
    idx = s.get("scene_index")
    audio = s.get("audio")
    bg = ASSETS/f"scene{idx}_bg.png"
    # fallback: use assets scene{idx}_bg.png
    # for characters, use Max and Sam as left/right always
    left = ASSETS/"Max.png"
    right = ASSETS/"Sam.png"
    out_scene_video = OUT/f"scene{idx}_animated.mp4"
    # ensure files exist
    if not bg.exists():
        print("Missing bg", bg, "-- skipping scene", idx)
        continue
    if not left.exists() or not right.exists():
        print("Missing character assets, skipping scene", idx)
        continue
    compose_frames_for_scene(idx, audio, bg, left, right, out_scene_video)

print("Lip-sync & build completed.")
