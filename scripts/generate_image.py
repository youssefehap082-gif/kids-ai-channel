# scripts/generate_image.py
import os, sys, requests, base64
HF_TOKEN = os.environ.get("HF_API_TOKEN")
MODEL = "prompthero/openjourney-v4"  # متاح عموماً، غيّره لو تحب
URL = f"https://api-inference.huggingface.co/models/{MODEL}"

def gen_image(prompt, outpath):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    payload = {"inputs": prompt}
    try:
        r = requests.post(URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        # some endpoints return raw image bytes
        if r.headers.get("content-type","").startswith("image/"):
            with open(outpath, "wb") as f:
                f.write(r.content)
            print("Saved direct image to", outpath)
            return
        # some return base64 inside json
        data = r.json()
        if isinstance(data, list) and len(data)>0 and "generated_image" in data[0]:
            b64 = data[0]["generated_image"]
            with open(outpath, "wb") as f:
                f.write(base64.b64decode(b64))
            print("Saved base64 image to", outpath)
            return
        # fallback: create placeholder
        raise Exception("Unknown image response")
    except Exception as e:
        print("Image generation failed:", e)
        # create simple placeholder using ffmpeg (requires ffmpeg installed)
        try:
            os.makedirs(os.path.dirname(outpath), exist_ok=True)
            # create 1280x720 light background with text via ImageMagick if available. Using ffmpeg color fallback:
            import subprocess
            subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=lightblue:s=1280x720","-frames:v","1",outpath], check=True)
        except Exception as ee:
            print("Fallback placeholder creation failed:", ee)
        print("Saved placeholder to", outpath)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/generate_image.py \"prompt\" output.png")
        sys.exit(1)
    prompt = sys.argv[1]
    out = sys.argv[2]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    gen_image(prompt, out)
