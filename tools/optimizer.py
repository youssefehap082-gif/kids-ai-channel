# tools/optimizer.py
import json, time
from pathlib import Path

WORKDIR = Path("workspace")
LOG = WORKDIR / "upload_log.json"

class AIOptimizer:
    def _init_(self):
        self.report_file = WORKDIR / "optimizer_report.json"

    def run(self):
        if not LOG.exists():
            report = {"time": time.ctime(), "message": "No uploads yet."}
            self.report_file.write_text(json.dumps(report, indent=2))
            return report
        try:
            data = json.loads(LOG.read_text())
        except:
            data = []
        stats = {}
        for item in data:
            a = item.get("animal", "unknown")
            stats[a] = stats.get(a, 0) + 1
        top = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
        rec = {
            "generated_at": time.ctime(),
            "top_uploaded_animals": top,
            "recommendation": "Focus on top animals and create variations (shorts + long)."
        }
        self.report_file.write_text(json.dumps(rec, indent=2))
        return rec
