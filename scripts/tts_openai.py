# scripts/tts_openai.py
import os, sys, json, time, random, subprocess
from pathlib import Path
import requests

API_KEY = os.environ.get("OPENAI_API_KEY", "")
OUT = Path("output")
SCRIPT_PATH = OUT / "script.json"
OUT.mkdir(exist_ok=True)

SPEAKER_VOICE_MAP = {
  "Max": "alloy",
  "Sam": "ash",
  "Lily": "fable",
  "Alex": "ballad",
  "Emma": "coral",
  "Owl": "echo",
  "Narrator": "alloy"
}
SPEAKER_PAN = {"Max": -0.25, "Sam": 0.25, "Lily": -0.2, "Alex": 0.2, "Emma": 0.0, "Owl": 0.0}

TTS_URL = "https://api.openai.com/v1/audio/speech"
MODEL = "gpt-4o-mini-tts"
MAX_RETRIES = 5

def log(*a):
    print(*a); sys.stdout.flush()

def call_openai_tts(text, voice, outpath):
    if not API_KEY:
        return False
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "Accept": "audio/mpeg"}
    payload = {"model": MODEL, "voice": voice, "input": text}
    for attempt in range(1, MAX_RETRIES+1):
        try:
            r = requests.post(TTS_URL, headers=headers, json=payload, stream=True, timeout=120)
            if r.status_code == 429:
                wait = (2 ** attempt) * (0.6 + random.random()*0.8)
                log(f"OpenAI 429 — sleeping {wait:.1f}s (attempt {attempt})")
                time.sleep(wait)
                continue
            r.raise_for_status()
            with open(outpath, "wb") as f:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            log("OpenAI TTS attempt failed:", e)
            time.sleep(1 + attempt)
    return False

def fallback_gtts(text, outpath):
    try:
        from gtts import gTTS
        log("Using gTTS fallback")
        t = gTTS(text, lang='en')
        t.save(outpath)
        return True
    except Exception as e:
        log("gTTS failed:", e)
        # create 1s silent mp3
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-t","1","-q:a","9","-acodec","libmp3lame", outpath], check=True)
        return True

def mp3_to_wav(mp3, wav):
    subprocess.run(["ffmpeg","-y","-i", mp3, "-ar","44100","-ac","2", wav], check=True)

def concat_wavs(wavs, out_wav):
    listf = OUT / "concat_list.txt"
    with open(listf, "w", encoding="utf-8") as f:
        for w in wavs:
            f.write(f"file '{str(Path(w).resolve())}'\n")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", out_wav], check=True)
    listf.unlink(missing_ok=True)

def pan_audio(in_mp3, pan, out_mp3):
    import math
    a = pan * (math.pi/4)
    c0 = f"cos({a})*c0+sin({a})*c1"
    c1 = f"sin({a})*c0+cos({a})*c1"
    tmp = OUT / (Path(out_mp3).stem + "_tmp.wav")
    subprocess.run(["ffmpeg","-y","-i", in_mp3, "-ar","44100","-ac","2", str(tmp)], check=True)
    subprocess.run(["ffmpeg","-y","-i", str(tmp), "-af", f"pan=stereo|c0={c0}|c1={c1}", str(tmp) + ".p.wav"], check=True)
    subprocess.run(["ffmpeg","-y","-i", str(tmp) + ".p.wav", "-codec:a","libmp3lame","-b:a","192k", out_mp3], check=True)
    Path(str(tmp) + ".p.wav").unlink(missing_ok=True)
    tmp.unlink(missing_ok=True)

def ffprobe_duration(path):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", path], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except Exception:
        return 0.0

def build_scene_audio(idx, dialogue):
    part_wavs = []
    for j, node in enumerate(dialogue, start=1):
        speaker = node.get("speaker","Narrator")
        text = node.get("text","").strip()
        if not text:
            continue
        voice = SPEAKER_VOICE_MAP.get(speaker, "alloy")
        mp3_path = OUT / f"scene{idx}_part{j}_{speaker.replace(' ','_')}.mp3"
        ok = call_openai_tts(text, voice, str(mp3_path))
        if not ok:
            log(f"OpenAI failed for {speaker} — using gTTS fallback")
            fallback_gtts(text, str(mp3_path))
        wav_path = str(OUT / f"scene{idx}_part{j}_{speaker.replace(' ','_')}.wav")
        try:
            mp3_to_wav(str(mp3_path), wav_path)
        except Exception as e:
            log("mp3->wav failed, creating silent wav", e)
            subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-t","1", wav_path], check=True)
        pan = float(SPEAKER_PAN.get(speaker, 0.0))
        if abs(pan) > 0.01:
            panned_mp3 = str(OUT / f"scene{idx}_part{j}_{speaker.replace(' ','_')}_panned.mp3")
            try:
                pan_audio(str(mp3_path), pan, panned_mp3)
                wav_path = str(OUT / f"scene{idx}_part{j}_{speaker.replace(' ','_')}_panned.wav")
                mp3_to_wav(panned_mp3, wav_path)
            except Exception as e:
                log("Panning failed:", e)
        part_wavs.append(wav_path)
    if part_wavs:
        scene_wav = str(OUT / f"scene{idx}.wav")
        concat_wavs(part_wavs, scene_wav)
        scene_mp3 = str(OUT / f"scene{idx}.mp3")
        subprocess.run(["ffmpeg","-y","-i", scene_wav, "-codec:a","libmp3lame","-b:a","192k", scene_mp3], check=True)
        # cleanup wavs
        for w in part_wavs:
            Path(w).unlink(missing_ok=True)
        Path(scene_wav).unlink(missing_ok=True)
        dur = ffprobe_duration(scene_mp3)
        log(f"Built scene {idx} audio -> {scene_mp3} (duration {dur:.2f}s)")
        return scene_mp3
    else:
        out_sil = str(OUT / f"scene{idx}_silent.mp3")
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-t","1","-q:a","9","-acodec","libmp3lame", out_sil], check=True)
        log(f"No dialogue for scene {idx}, created silent audio {out_sil}")
        return out_sil

def main():
    if not SCRIPT_PATH.exists():
        print("Missing output/script.json — run generate_script.py first.")
        sys.exit(1)
    data = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    manifest = {"title": data.get("title","Auto"), "scenes": []}
    for idx, sc in enumerate(data.get("scenes",[]), start=1):
        dialogue = sc.get("dialogue", [])
        if not dialogue:
            dialogue = [{"speaker":"Narrator","text": sc.get("summary","Short scene.")}]
        log(f"Processing scene {idx} with {len(dialogue)} lines...")
        mp3 = build_scene_audio(idx, dialogue)
        manifest["scenes"].append({"scene_index": idx, "audio": mp3, "image_prompt": sc.get("image_prompt","")})
    (OUT / "scene_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    log("Saved output/scene_manifest.json")

if __name__ == "__main__":
    main()
