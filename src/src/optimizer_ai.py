import os, csv, json, math, re, time, random
from datetime import datetime, timezone
from collections import defaultdict, Counter
from pathlib import Path

from src.youtube import list_recent_videos, get_video_stats_bulk
from src.utils import get_trending_animals

STATS_CSV = Path("stats.csv")
MODEL_JSON = Path("model.json")

# كلمات مفتاحية بسيطة لاستخراج اسم الحيوان من العنوان
ANIMAL_WORDS = [
    "lion","tiger","elephant","panda","giraffe","zebra","koala","penguin","eagle","owl",
    "shark","dolphin","wolf","fox","bear","crocodile","hippo","rhino","leopard",
    "cheetah","kangaroo","camel","otter","seal","whale","octopus","turtle","cobra","python",
    "komodo dragon","jaguar","lynx","boar","gazelle","antelope","buffalo","moose","reindeer",
    "flamingo","peacock","parrot","falcon","sparrow","raven","owl","bee","butterfly","manta ray",
    "stingray","gorilla","chimpanzee","orangutan","sloth","meerkat","hedgehog","badger","beaver"
]
ANIMAL_WORDS_LOWER = [w.lower() for w in ANIMAL_WORDS]

def _extract_animal(title: str) -> str:
    t = title.lower()
    # ابحث عن تطابق دقيق أولاً
    for w in sorted(ANIMAL_WORDS_LOWER, key=len, reverse=True):
        if w in t:
            return w
    # محاكاة استخراج عام (كلمة قبل/بعد "the")
    m = re.search(r"facts about the ([a-z\s\-]+)", t)
    if m:
        return m.group(1).strip()
    return ""

def _read_stats_csv():
    rows = []
    if STATS_CSV.exists():
        with open(STATS_CSV, newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            for row in r:
                if len(row) >= 6:
                    rows.append({
                        "ts": row[0], "video_id": row[1], "title": row[2],
                        "animal": row[3], "views": int(row[4]), "likes": int(row[5]),
                        "is_short": row[6] if len(row) > 6 else "0"
                    })
    return rows

def _write_stats_rows(rows):
    header_needed = not STATS_CSV.exists()
    with open(STATS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if header_needed:
            w.writerow(["timestamp","video_id","title","animal","views","likes","is_short"])
        for r in rows:
            w.writerow([r["ts"], r["video_id"], r["title"], r["animal"], r["views"], r["likes"], r.get("is_short","0")])

def record_video_result(video_id: str, title: str, is_short: bool):
    """يُسجل فيديو جديد فور الرفع بقيم مؤقتة (0)؛ هنحدّثها لاحقًا في التتبع اليومي."""
    animal = _extract_animal(title) or "unknown"
    row = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "video_id": video_id, "title": title, "animal": animal,
        "views": 0, "likes": 0, "is_short": "1" if is_short else "0"
    }
    _write_stats_rows([row])

def refresh_channel_stats(limit=50):
    """يسحب أحدث فيديوهات القناة ويحدث stats.csv بالمشاهدات والإعجابات."""
    videos = list_recent_videos(limit=limit)
    ids = [v["id"] for v in videos]
    stats_map = get_video_stats_bulk(ids)  # {id: {"views":..,"likes":..}}
    rows = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for v in videos:
        title = v.get("title","")
        animal = _extract_animal(title) or "unknown"
        st = stats_map.get(v["id"], {"views":0,"likes":0})
        rows.append({
            "ts": ts, "video_id": v["id"], "title": title, "animal": animal,
            "views": int(st.get("views",0)), "likes": int(st.get("likes",0)),
            "is_short": "1" if v.get("is_short", False) else "0"
        })
    _write_stats_rows(rows)
    return rows

def _engagement_score(views:int, likes:int) -> float:
    # وزن بسيط: اللايك بـ 20 مشاهدة تقريبًا
    return views + 20*likes

def train_weekly_model():
    """يبني نموذج بسيط (Top-N) لأفضل الحيوانات أداءً خلال الأسبوع الأخير ويحفظه في model.json"""
    rows = _read_stats_csv()
    if not rows:
        MODEL_JSON.write_text(json.dumps({"top_animals": [], "ts": datetime.utcnow().isoformat()}))
        return {"top_animals": []}

    # آخر 7 أيام
    cutoff = time.time() - 7*24*3600
    weekly = []
    for r in rows:
        try:
            t = datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            t = time.time()
        if t >= cutoff:
            weekly.append(r)

    agg = defaultdict(lambda: {"views":0,"likes":0})
    for r in weekly:
        k = r["animal"]
        agg[k]["views"] += r["views"]
        agg[k]["likes"] += r["likes"]

    scored = []
    for animal, x in agg.items():
        scored.append((animal, _engagement_score(x["views"], x["likes"])))
    scored.sort(key=lambda z: z[1], reverse=True)

    top = [a for a,score in scored if a and a!="unknown"][:15]
    # لو فاضية خالص، استعن بالترند العام
    if not top:
        top = get_trending_animals()[:10]

    data = {"top_animals": top, "ts": datetime.utcnow().isoformat()}
    MODEL_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data

def recommend_next_animals(n_long=4, n_short=8):
    """يوصي بقائمة حيوانات للإنتاج القادم (يمزج أفضل ما نجح + ترند الأسبوع)."""
    model = {}
    if MODEL_JSON.exists():
        try:
            model = json.loads(MODEL_JSON.read_text())
        except Exception:
            model = {}
    top = model.get("top_animals", [])
    trend = get_trending_animals()

    pool = []
    # أعطِ أفضلية كبيرة للـ top
    for a in top:
        pool += [a]*3
    # ثم الترند
    pool += trend
    # ونضف شوية تنويع
    pool += ["sea turtle","polar bear","orca","seal","lynx","falcon","raccoon","lemur","jellyfish"]

    # فلترة تكرارات الأسبوع الحالي (من stats.csv)
    rows = _read_stats_csv()
    week_animals = set()
    cutoff = time.time() - 7*24*3600
    for r in rows:
        try:
            t = datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            if t >= cutoff and r["animal"]:
                week_animals.add(r["animal"])
        except: pass

    # اختيارات نهائية
    random.shuffle(pool)
    uniq = []
    for a in pool:
        al = a.lower()
        if al not in week_animals and al not in uniq and re.search(r"[a-z]", al):
            uniq.append(al)
        if len(uniq) >= max(n_long, n_short):
            break

    # رجّع قائمتين: للّونج وللشورتس
    need_long = uniq[:n_long]
    need_short = (uniq[n_long:n_long+n_short] or uniq[:n_short])
    return need_long, need_short

def daily_optimize():
    """Pipeline: يحدث الإحصائيات -> يدرب الموديل -> يطبع توصيات للإنتاج التالي."""
    print("📊 Refreshing channel stats…")
    refresh_channel_stats(limit=80)
    print("🧠 Training weekly model…")
    data = train_weekly_model()
    print(f"🏆 Top animals this week: {', '.join(data.get('top_animals',[])) or 'N/A'}")
    long_list, short_list = recommend_next_animals()
    print(f"🗓️ Recommended next LONG videos: {', '.join(long_list)}")
    print(f"🗓️ Recommended next SHORTS: {', '.join(short_list)}")
    # ترجيع القوائم علشان لو عايز تستعملها مباشرة في main
    return long_list, short_list
