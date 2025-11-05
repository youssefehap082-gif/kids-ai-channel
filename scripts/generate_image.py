# scripts/generate_image.py
import os, sys, requests, base64, subprocess
HF_TOKEN = os.environ.get("HF_API_TOKEN", "")
MODEL = "prompthero/openjourney-v4"
URL = f"https://api-inference.huggingface.co/models/{MODEL}"

if len(sys.argv) < 3:
    print("Usage: python3 scripts/generate_image.py \"prompt\" output.png")
    sys.exit(1)
prompt = sys.argv[1]
outpath = sys.argv[2]
os.makedirs(os.path.dirname(outpath) or ".", exist_ok=True)

def placeholder(path):
    try:
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=lightblue:s=1280x720","-frames:v","1",path], check=True)
        return True
    except Exception as e:
        print("Couldn't create placeholder:", e)
        return False

if HF_TOKEN:
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        r = requests.post(URL, headers=headers, json={"inputs": prompt}, timeout=120)
        r.raise_for_status()
        if r.headers.get("content-type","").startswith("image/"):
            open(outpath,"wb").write(r.content)
            print("Saved image to", outpath)
        else:
            data = r.json()
            if isinstance(data, list) and "generated_image" in data[0]:
                open(outpath,"wb").write(base64.b64decode(data[0]["generated_image"]))
                print("Saved image (base64) to", outpath)
            else:
                print("HF returned unknown image response, using placeholder.")
                placeholder(outpath)
    except Exception as e:
        print("HF image failed:", e)
        placeholder(outpath)
else:
    print("No HF token: creating placeholder image.")
    placeholder(outpath)
