import json, time
from pathlib import Path

WORKDIR = Path("workspace")

class AIOptimizer:
    def _init_(self):
        self.report = WORKDIR / "optimizer_report.json"

    def run(self):
        log = WORKDIR / "upload_log.json"
        if not log.exists():
            data = []
        else:
            data = json.loads(log.read_text())
        # تحليل بسيط: أكثر الحيوانات تكرارًا
        stats = {}
        for v in data:
            a = v.get("animal")
            stats[a] = stats.get(a, 0) + 1
        top = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]
        report = {
            "time": time.ctime(),
            "most_uploaded": top,
            "recommendation": f"Focus on animals like {', '.join([x[0] for x in top])} with better engagement.",
        }
        self.report.write_text(json.dumps(report, indent=2))
        return report
