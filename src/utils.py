import os, re, json, random, requests
from datetime import datetime, timedelta

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

# -------- Trending animals (weekly) --------
def get_trending_animals():
    """
    Returns a weekly-rotating list of popular animals.
    If OpenAI is available, generate fresh list; otherwise fallback to static pool.
    """
    pool = [
        "Lion","Elephant","Tiger","Giant Panda","Cheetah","Shark","Eagle","Owl",
        "Dolphin","Penguin","Giraffe","Koala","Crocodile","Komodo Dragon","King Cobra",
        "Snow Leopard","Humpback Whale","Sea Turtle","Octopus","Wolf","Fox","Bear","Hippo","Rhino"
    ]
    try:
        prompt = (
            "List 30 animal species that are currently popular in English YouTube searches. "
            "Return a plain comma-separated list without numbering."
        )
        r = requests.post(OPENAI_CHAT_URL, headers=HEADERS, json={
            "model":"gpt-4o-mini",
            "messages":[{"role":"user","content":prompt}],
            "temperature":0.6
        }, timeout=60)
        r.raise_for_status()
        txt = r.json()["choices"][0]["message"]["content"]
        items = [x.strip() for x in re.split(r"[,\n]+", txt) if x.strip()]
        items = [re.sub(r"[^A-Za-z \-]", "", x).strip() for x in items]
        items = [x for x in items if x]
        random.shuffle(items)
        return items[:30] if items else random.sample(pool, k=15)
    except Exception:
        random.shuffle(pool)
        return pool[:15]

# -------- Facts (10 bullets) --------
def get_animal_facts(animal: str):
    prompt = (
        f"Give exactly 10 short, accurate, engaging facts about the {animal}. "
        "One sentence per fact, <=20 words, neutral educational tone, no numbering."
    )
    r = requests.post(OPENAI_CHAT_URL, headers=HEADERS, json={
        "model":"gpt-4o-mini",
        "messages":[{"role":"user","content":prompt}],
        "temperature":0.5
    }, timeout=60)
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"]
    facts = [f.strip(" -•") for f in re.split(r"[\n]+", txt) if f.strip()]
    # enforce exactly 10
    return facts[:10] if len(facts) >= 10 else facts + [""]*(10-len(facts))

# -------- Hashtags (smart) --------
def generate_hashtags(animal: str, count: int = 10):
    prompt = (
        f"Create {count} YouTube hashtags for an English wildlife facts video about the {animal}. "
        "Return a space-separated single line."
    )
    try:
        r = requests.post(OPENAI_CHAT_URL, headers=HEADERS, json={
            "model":"gpt-4o-mini",
            "messages":[{"role":"user","content":prompt}],
            "temperature":0.4
        }, timeout=40)
        r.raise_for_status()
        line = r.json()["choices"][0]["message"]["content"].replace("\n"," ").strip()
        # sanitize
        tags = [t if t.startswith("#") else f"#{t}" for t in re.split(r"\s+", line) if t]
        # keep only words/#
        tags = [re.sub(r"[^#A-Za-z0-9_]", "", t) for t in tags]
        tags = [t for t in tags if len(t) > 1]
        return " ".join(tags[:count])
    except Exception:
        fallback = ["#Wildlife","#Animals","#Nature","#AnimalFacts","#Documentary","#Learn","#Education","#Eco","#Planet","#Discover"]
        return " ".join(fallback[:count])

# -------- AI Thumbnail (DALL·E) --------
def generate_thumbnail_ai(animal: str) -> str:
    """
    Generates a 1280x720 thumbnail via OpenAI images API and returns local path.
    """
    try:
        prompt = (
            f"High-impact YouTube thumbnail of a realistic {animal} close-up, dramatic lighting, "
            "documentary style, sharp focus, cinematic composition, 1280x720."
        )
        r = requests.post(OPENAI_IMAGE_URL, headers=HEADERS, json={
            "model":"gpt-image-1",
            "prompt": prompt,
            "size":"1280x720"
        }, timeout=120)
        r.raise_for_status()
        b64 = r.json()["data"][0]["b64_json"]
        import base64, tempfile
        path = os.path.join(tempfile.gettempdir(), f"thumb_{re.sub(r'\\W+','_',animal.lower())}.png")
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        return path
    except Exception as e:
        # Fallback single-color thumbnail with PIL text
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB",(1280,720),(30,30,30))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 92)
        except:
            font = ImageFont.load_default()
        text = animal.upper()
        if hasattr(d,"textbbox"):
            bbox = d.textbbox((0,0),text,font=font); w=bbox[2]-bbox[0]; h=bbox[3]-bbox[1]
        else:
            w,h = d.textsize(text,font=font)
        d.text(((1280-w)//2,(720-h)//2), text, fill=(240,240,240), font=font)
        fallback_path = os.path.join("/tmp", f"thumb_{re.sub(r'\\W+','_',animal.lower())}.png")
        img.save(fallback_path)
        return fallback_path
