# generate single image from prompt using Hugging Face text-to-image inference
import os, requests, sys, base64
HF_TOKEN = os.environ.get("HF_API_TOKEN")
MODEL = "stabilityai/stable-diffusion-2-1"

def gen(prompt, outpath):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {"inputs": prompt}
    r = requests.post(f"https://api-inference.huggingface.co/models/{MODEL}", headers=headers, json=data)
    r.raise_for_status()
    # some HF image endpoints return raw bytes; write content
    with open(outpath, "wb") as f:
        f.write(r.content)
    print("Saved", outpath)

if __name__ == "__main__":
    prompt = sys.argv[1]
    out = sys.argv[2]
    gen(prompt, out)
