# scripts/tts_openai.py
import os, sys, json, requests, subprocess, tempfile

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("ERROR: OPENAI_API_KEY not set as environment variable.")

SCRIPT_PATH = "output/script.json"
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

# Set the voice mapping for characters (edit to your liking)
SPEAKER_VOICE_MAP = {
    "Hazem": "alloy",        # male
    "Sheh Madwar": "ash",    # male 2
    "Hind": "fable",         # female
    "Alaa": "ballad",        # male 3
    "Eman": "coral"          # female 2
}

# Optional: panning per speaker (left/right balance -1.0..1.0)
SPEAKER_PAN = {
    "Hazem": -0.3,
    "Sheh Madwar": 0.3,
    "Hind": -0.2,
    "Alaa": 0.2,
    "Eman": 0.0
}

def tts_request(text, voice, outpath):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": voice,
        "input": text
    }
    print(f"Request TTS voice={voice} len={len(text)} -> {outpath}")
    r = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
    r.raise_for_status()
    with open(outpath, "wb") as f:
        for chunk in r.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    return outpath

def make_wav_from_mp3(mp3_path, wav_path):
    cmd = ["ffmpeg","-y","-i", mp3_path, "-ar","44100","-ac","2","-sample_fmt","s16", wav_path]
    subprocess.run(cmd, check=True)

def concat_wavs(wav_list, out_wav):
    # create list file
    list_file = tempfile.mktemp(suffix=".txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for w in wav_list:
            f.write(f"file '{os.path.abspath(w)}'\n")
    cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i", list_file, "-c","copy", out_wav]
    subprocess.run(cmd, check=True)
    os.remove(list_file)

def apply_panning(input_mp3, pan_value, out_mp3):
    # pan_value between -1 (left) and 1 (right). We'll use stereo pan filter.
    # convert to wav, apply pan, re-encode
    tmp_wav = tempfile.mktemp(suffix=".wav")
    cmd1 = ["ffmpeg","-y","-i", input_mp3, "-ar","44100","-ac","2", tmp_wav]
    subprocess.run(cmd1, check=True)
    # ffmpeg pan filter: stereo, left gain = (1 - p)/2? we'll use simple approach: pan=stereo|c0=c0*(1-p)/1 ... approximate using "pan=stereo|c0=FL*(1-p)+FR*p ..."
    # Simpler approach: use "pan=stereo|c0=0.5*FL+0.5*FR" won't change. For mild panning, use "adelay" is complex.
    # We'll use 'pan=stereo|c0=cos(a)*c0+sin(a)*c1|c1=sin(a)*c0+cos(a)*c1' where a = pan_value*(pi/4)
    import math
    a = pan_value * (math.pi/4)
    c0 = f"cos({a})*c0+sin({a})*c1"
    c1 = f"sin({a})*c0+cos({a})*c1"
    out_wav = tempfile.mktemp(suffix=".wav")
    cmd2 = ["ffmpeg","-y","-i", tmp_wav, "-af", f"pan=stereo|c0={c0}|c1={c1}", out_wav]
    subprocess.run(cmd2, check=True)
    # back to mp3
    cmd3 = ["ffmpeg","-y","-i", out_wav, "-codec:a","libmp3lame","-b:a","192k", out_mp3]
    subprocess.run(cmd3, check=True)
    # cleanup
    os.remove(tmp_wav)
    os.remove(out_wav)

def make_scene_audio(scene_idx, dialogue_list):
    part_mp3s = []
    part_wavs = []
    for j, node in enumerate(dialogue_list):
        speaker = node.get("speaker","Narrator")
        text = node.get("text","")
        voice = SPEAKER_VOICE_MAP.get(speaker, "alloy")
        part_mp3 = f"{OUT_DIR}/scene{scene_idx}_part{j+1}_{speaker.replace(' ','_')}.mp3"
        # request TTS
        tts_request(text, voice, part_mp3)
        # optional: apply light normalization/volume
        norm_mp3 = f"{OUT_DIR}/scene{scene_idx}_part{j+1}_{speaker.replace(' ','_')}_norm.mp3"
        # convert to wav for concatenation
        wav_path = f"{OUT_DIR}/scene{scene_idx}_part{j+1}_{speaker.replace(' ','_')}.wav"
        make_wav_from_mp3(part_mp3, wav_path)
        # apply mild panning if desired
        pan_val = SPEAKER_PAN.get(speaker, 0.0)
        if abs(pan_val) > 0.01:
            panned_mp3 = f"{OUT_DIR}/scene{scene_idx}_part{j+1}_{speaker.replace(' ','_')}_panned.mp3"
            apply_panning(part_mp3, pan_val, panned_mp3)
            # regenerate wav from panned mp3
            os.remove(wav_path)
            make_wav_from_mp3(panned_mp3, wav_path)
            os.remove(panned_mp3)
        part_mp3s.append(part_mp3)
        part_wavs.append(wav_path)

    # concat wavs to one scene wav
    scene_wav = f"{OUT_DIR}/scene{scene_idx}.wav"
    concat_wavs(part_wavs, scene_wav)
    # encode to mp3
    scene_mp3 = f"{OUT_DIR}/scene{scene_idx}.mp3"
    subprocess.run(["ffmpeg","-y","-i", scene_wav, "-codec:a","libmp3lame","-b:a","192k", scene_mp3], check=True)
    # cleanup intermediate wavs
    for w in part_wavs:
        if os.path.exists(w):
            os.remove(w)
    if os.path.exists(scene_wav):
        os.remove(scene_wav)
    print("Built scene audio:", scene_mp3)
    return scene_mp3

def main():
    if not os.path.exists(SCRIPT_PATH):
        raise SystemExit("Script JSON not found at output/script.json. Run generate_script.py first.")
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data.get("scenes", [])
    if not scenes:
        raise SystemExit("No scenes in script.json")

    scene_mp3_files = []
    for idx, sc in enumerate(scenes, start=1):
        dialogue = sc.get("dialogue", [])
        if len(dialogue) == 0:
            # fallback: use a single narrator line if no dialogue
            txt = sc.get("summary", "") or sc.get("text", "") or "A short scene."
            dialogue = [{"speaker":"Narrator","text":txt}]
        mp3 = make_scene_audio(idx, dialogue)
        scene_mp3_files.append((mp3, sc.get("image_prompt","")))

    # write scene manifest for later steps
    manifest = {"title": data.get("title","Auto Episode"), "scenes": []}
    for i,(mp3, imgprompt) in enumerate(scene_mp3_files, start=1):
        manifest["scenes"].append({"scene_index": i, "audio": mp3, "image_prompt": imgprompt})
    with open(OUT_DIR + "/scene_manifest.json","w",encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("Saved scene manifest to output/scene_manifest.json")

if __name__ == "__main__":
    main()
