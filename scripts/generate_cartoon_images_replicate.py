# scripts/generate_cartoon_images_replicate.py
import os, json, time, requests
from pathlib import Path

# requires `pip install replicate`
try:
    import replicate
except Exception as e:
    raise SystemExit("Missing python package 'replicate'. Install with: pip install replicate")

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "").strip()
if not REPLICATE_TOKEN:
    print("Warning: REPLICATE_API_TOKEN not set. Exiting.")
    raise SystemExit(1)

replicate_client = replicate.Client(api_token=REPLICATE_TOKEN)

OUT = Path("output")
ASSETS = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

prompts_path = OUT / "prompts.json"
if not prompts_path.exists():
    print("Missing output/prompts.json — run generate_script_and_prompts.py first")
    raise SystemExit(1)

prompts = json.load(open(prompts_path, encoding="utf-8"))

# helper to download output URL
def download_url(url, dest:Path):
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print("Saved", dest)

# main loop
for item in prompts:
    idx = item["scene_index"]
    base_query = item.get("search_query","cute cat scene")
    # craft a targeted prompt for SDXL to produce a high-quality cartoon-style frame
    prompt = (
        f"{base_query}, ultra-detailed 2D cartoon, studio lighting, high detail, bold clean lineart, "
        "bright saturated colors, expressive characters, cinematic composition, 4k, "
        "children's storybook illustration style, charming, cute, character-focused, full body "
        "— emphasize clear silhouettes and readable facial expressions"
    )
    print(f"Generating scene {idx} image with prompt:\n{prompt}\n")

    try:
        # use replicate.run with the public model string
        # This will run the SDXL model on Replicate (may cost small credits)
        output = replicate.run(
            "stability-ai/sdxl",
            input={"prompt": prompt, "width": 1280, "height": 720}
        )
        # output might be list of urls or single url
        if isinstance(output, list) and len(output) > 0:
            url = output[0]
        else:
            url = output
        if not url:
            raise Exception("No output URL returned from Replicate")
        out_path = ASSETS / f"scene{idx}_bg.png"
        download_url(url, out_path)
        time.sleep(1.0)  # polite spacing
    except Exception as e:
        print("Error generating scene", idx, ":", e)
        # don't fail hard — we will proceed and let fallback create image later
