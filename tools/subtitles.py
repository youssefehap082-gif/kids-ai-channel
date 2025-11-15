from pathlib import Path
def write_simple_srt(lines, out_path, start_offset=0.0, line_duration=3.0):
    def fmt_time(t):
        ms = int((t - int(t)) * 1000)
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    out = []
    t = float(start_offset)
    idx = 1
    for ln in lines:
        start = t; end = t + line_duration
        out.append(f"{idx}"); out.append(f"{fmt_time(start)} --> {fmt_time(end)}"); out.append(ln); out.append("")
        idx += 1; t = end
    Path(out_path).write_text("\n".join(out), encoding='utf-8'); return out_path
