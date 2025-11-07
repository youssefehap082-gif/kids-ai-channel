# scripts/generate_images_replicate.py
import os, json, time, requests
from pathlib import Path

try:
    import replicate
except Exception:
    raise SystemExit("Install replicate: pip install replicate")

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "").strip()
if not REPLICATE_TOKEN:
    raise SystemExit("REPLICATE_API_TOKEN not set in env")

client = replicate.Client(api_token=REPLICATE_TOKEN)

OUT = Path("output")
ASSETS = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

prompts_path = OUT / "prompts.json"
if not prompts_path.exists():
    raise SystemExit("Missing output/prompts.json — run generate_story.py first")

prompts = json.load(open(prompts_path, encoding="utf-8"))

def download_url(url, dest:Path):
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print("Saved", dest)

for item in prompts:
    idx = item["scene_index"]
    base_prompt = item.get("prompt","cute cartoon scene")
    prompt = (
        f"{base_prompt}. Ultra-detailed 2D storybook cartoon, bold clean lineart, expressive character, soft cinematic lighting, high detail, 1280x720"
    )
    print(f"[Replicate] Scene {idx} prompt:\n{prompt}\n")
    try:
        # NOTE: model slug may change on Replicate. If this fails, check model name on replicate.com
        output = client.run("stability-ai/stable-diffusion-xl", input={"prompt": prompt, "width":1280, "height":720})
        if isinstance(output, list):
            url = output[0]
        else:
            url = output
        if not url:
            raise Exception("No URL returned from replicate")
        out_path = ASSETS / f"scene{idx}_bg.png"
        download_url(url, out_path)
        time.sleep(1.0)
    except Exception as e:
        print("Replicate error for scene", idx, ":", e)
        # continue; prepare_assets.py will create fallback if missing
