# scripts/tts_openai.py  (UPDATED - robust retries + fallback)
import os
import sys
import json
import time
import math
import random
import subprocess
import requests
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("ERROR: OPENAI_API_KEY not set as environment variable.")

OUT_DIR = Path("output")
SCRIPT_PATH = OUT_DIR / "script.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# mapping speakers -> OpenAI voice names (edit to taste)
SPEAKER_VOICE_MAP = {
    "Hazem": "alloy",
    "Sheh Madwar": "ash",
    "Hind": "fable",
    "Alaa": "ballad",
    "Eman": "coral",
    "Narrator": "alloy"
}

# panning per speaker (-1.0 left ... 1.0 right)
SPEAKER_PAN = {
    "Hazem": -0.3,
    "Sheh Madwar": 0.3,
    "Hind": -0.2,
    "Alaa": 0.2,
    "Eman": 0.0
}

# OpenAI TTS endpoint & model
OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"
OPENAI_MODEL = "gpt-4o-mini-tts"

# Retry settings for OpenAI requests
MAX_RETRIES = 5
BASE_SLEEP = 1.5  # base seconds for exponential backoff
TIMEOUT = 120

def log(*a, **k):
    print(*a, **k)
    sys.stdout.flush()

def write_streamed_response(resp, outpath):
    with open(outpath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)

def generate_tts_openai(text, voice, outpath):
    """
    Generate mp3 via OpenAI TTS with retries and exponential backoff.
    Returns True on success, False on failure.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {"model": OPENAI_MODEL, "voice": voice, "input": text}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log(f"Attempt {attempt}/{MAX_RETRIES} - TTS request (voice={voice}) len={len(text)}")
            resp = requests.post(OPENAI_TTS_URL, headers=headers, json=payload, stream=True, timeout=TIMEOUT)
            if resp.status_code == 429:
                # Too Many Requests -> exponential backoff with jitter
                wait = BASE_SLEEP * (2 ** (attempt - 1))
                wait = wait * (0.8 + 0.4 * random.random())  # jitter
                log(f"Got 429 Too Many Requests — sleeping {wait:.1f}s then retrying...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            # successful -> stream to file
            write_streamed_response(resp, outpath)
            log("Saved TTS to", outpath)
            return True
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            text_excerpt = ""
            try:
                text_excerpt = e.response.text[:400]
            except Exception:
                pass
            log(f"HTTPError on attempt {attempt}: {e} status={status} excerpt={text_excerpt}")
            if status and 500 <= status < 600:
                # server error -> retry after backoff
                wait = BASE_SLEEP * (2 ** (attempt - 1))
                log(f"Server error, sleeping {wait:.1f}s then retrying...")
                time.sleep(wait)
                continue
            # other HTTP errors, don't retry many times (but try a couple times)
            if attempt < MAX_RETRIES:
                time.sleep(BASE_SLEEP)
                continue
            return False
        except Exception as e:
            log(f"Exception during TTS request on attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(BASE_SLEEP * (2 ** (attempt - 1)))
                continue
            return False
    return False

def fallback_with_gtts(text, outpath):
    """
    Try to use gTTS as fallback (free). If gTTS not installed, create a short silent mp3 fallback.
    Returns True if created some audio file.
    """
    try:
        from gtts import gTTS
        log("Using gTTS fallback...")
        t = gTTS(text, lang='en')
        t.save(outpath)
        log("Saved fallback gTTS to", outpath)
        return True
    except Exception as e:
        log("gTTS fallback failed or not installed:", e)
        # create 2-second silence so pipeline continues
        try:
            log("Creating 2s silent mp3 fallback using ffmpeg...")
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-t", "2", "-q:a", "9", "-acodec", "libmp3lame", outpath
            ], check=True)
            log("Saved silent fallback to", outpath)
            return True
        except Exception as ee:
            log("Failed to create silent fallback:", ee)
            return False

def make_wav_from_mp3(mp3_path, wav_path):
    subprocess.run(["ffmpeg","-y","-i", mp3_path, "-ar","44100","-ac","2","-sample_fmt","s16", wav_path], check=True)

def concat_wavs(wav_list, out_wav):
    # create a temporary list file
    list_file = OUT_DIR / "concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for w in wav_list:
            f.write(f"file '{str(Path(w).resolve())}'\n")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(list_file), "-c","copy", out_wav], check=True)
    list_file.unlink(missing_ok=True)

def apply_panning(input_mp3, pan_value, out_mp3):
    # pan_value between -1 and 1; use a mild stereo pan transformation
    import math
    a = pan_value * (math.pi/4)
    # build filter using cos/sin (safe expression)
    c0 = f"cos({a})*c0+sin({a})*c1"
    c1 = f"sin({a})*c0+cos({a})*c1"
    tmp_wav = OUT_DIR / (Path(out_mp3).stem + "_tmp.wav")
    # convert to wav then apply pan
    subprocess.run(["ffmpeg","-y","-i", input_mp3, "-ar","44100","-ac","2", str(tmp_wav)], check=True)
    subprocess.run(["ffmpeg","-y","-i", str(tmp_wav), "-af", f"pan=stereo|c0={c0}|c1={c1}", str(tmp_wav) + ".panned.wav"], check=True)
    subprocess.run(["ffmpeg","-y","-i", str(tmp_wav) + ".panned.wav", "-codec:a","libmp3lame","-b:a","192k", out_mp3], check=True)
    # cleanup
    try:
        Path(str(tmp_wav) + ".panned.wav").unlink(missing_ok=True)
        tmp_wav.unlink(missing_ok=True)
    except Exception:
        pass

def make_scene_audio(scene_idx, dialogue_list):
    part_mp3s = []
    part_wavs = []
    for j, node in enumerate(dialogue_list):
        speaker = node.get("speaker","Narrator")
        text = node.get("text","").strip()
        if not text:
            continue
        voice = SPEAKER_VOICE_MAP.get(speaker, "alloy")
        part_mp3 = OUT_DIR / f"scene{scene_idx}_part{j+1}_{speaker.replace(' ','_')}.mp3"
        success = generate_tts_openai(text, voice, str(part_mp3))
        if not success:
            # fallback to gTTS or silence
            log(f"OpenAI TTS failed for speaker={speaker}. Attempting fallback.")
            ok = fallback_with_gtts(text, str(part_mp3))
            if not ok:
                log(f"Fallback also failed for part {part_mp3}. Continuing with silent placeholder.")
        # convert to wav for concatenation
        wav_path = OUT_DIR / f"scene{scene_idx}_part{j+1}_{speaker.replace(' ','_')}.wav"
        try:
            make_wav_from_mp3(str(part_mp3), str(wav_path))
        except Exception as e:
            log("Failed to convert mp3 to wav, creating short silent wav as fallback:", e)
            # create 1s silence wav
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-t", "1", str(wav_path)
            ], check=True)
        # apply panning if defined
        pan_val = float(SPEAKER_PAN.get(speaker, 0.0))
        if abs(pan_val) > 0.01:
            panned_mp3 = OUT_DIR / f"scene{scene_idx}_part{j+1}_{speaker.replace(' ','_')}_panned.mp3"
            try:
                apply_panning(str(part_mp3), pan_val, str(panned_mp3))
                # recreate wav from panned mp3
                wav_path.unlink(missing_ok=True)
                make_wav_from_mp3(str(panned_mp3), str(wav_path))
                # cleanup panned mp3
                panned_mp3.unlink(missing_ok=True)
            except Exception as e:
                log("Panning failed, ignoring panning for this part:", e)
        part_mp3s.append(str(part_mp3))
        part_wavs.append(str(wav_path))

    # concat wavs to one scene wav
    scene_wav = OUT_DIR / f"scene{scene_idx}.wav"
    if part_wavs:
        concat_wavs(part_wavs, str(scene_wav))
        scene_mp3 = OUT_DIR / f"scene{scene_idx}.mp3"
        subprocess.run(["ffmpeg","-y","-i", str(scene_wav), "-codec:a","libmp3lame","-b:a","192k", str(scene_mp3)], check=True)
        # cleanup intermediate wavs
        for w in part_wavs:
            try:
                Path(w).unlink(missing_ok=True)
            except Exception:
                pass
        try:
            scene_wav.unlink(missing_ok=True)
        except Exception:
            pass
        log("Built scene audio:", str(scene_mp3))
        return str(scene_mp3)
    else:
        # no parts -> create tiny silent mp3 so pipeline continues
        out_silent = OUT_DIR / f"scene{scene_idx}.mp3"
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-t","1","-q:a","9","-acodec","libmp3lame", str(out_silent)], check=True)
        log("No dialogue for scene, created silent audio:", str(out_silent))
        return str(out_silent)

def main():
    if not SCRIPT_PATH.exists():
        log("Script not found at", SCRIPT_PATH, "- run generate_script.py first.")
        sys.exit(1)
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenes = data.get("scenes", [])
    if not scenes:
        log("No scenes in script.json")
        sys.exit(1)

    manifest = {"title": data.get("title","Auto Episode"), "scenes": []}
    for idx, sc in enumerate(scenes, start=1):
        dialogue = sc.get("dialogue", [])
        if not dialogue:
            # fallback single narrator line if none provided
            text = sc.get("summary") or sc.get("text") or "A short scene."
            dialogue = [{"speaker":"Narrator","text":text}]
        log(f"Building audio for scene {idx} with {len(dialogue)} lines...")
        try:
            mp3 = make_scene_audio(idx, dialogue)
            manifest["scenes"].append({"scene_index": idx, "audio": mp3, "image_prompt": sc.get("image_prompt","")})
        except Exception as e:
            log("Failed to build scene audio:", e)
            # still append a silent audio so later steps don't break
            silent = OUT_DIR / f"scene{idx}_silent.mp3"
            subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-t","1","-q:a","9","-acodec","libmp3lame", str(silent)], check=True)
            manifest["scenes"].append({"scene_index": idx, "audio": str(silent), "image_prompt": sc.get("image_prompt","")})

    with open(OUT_DIR / "scene_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    log("Saved scene manifest to", OUT_DIR / "scene_manifest.json")

if __name__ == "__main__":
    main()
