# captions_uploader.py
# Create SRT captions from the script and upload them to YouTube (helper).
# Includes optional forced-alignment via aeneas if installed.

from pathlib import Path
import re
import math
import shutil

def seconds_to_srt_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s - int(s)) * 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"

def create_srt_from_script(script_text, duration, out_path: Path):
    """
    Very simple SRT: split script into sentences and distribute evenly across duration.
    script_text: full script (string)
    duration: video duration in seconds (float)
    out_path: Path to write .srt
    """
    sentences = re.split(r'(?<=[.!?])\s+', script_text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        out_path.write_text('')
        return out_path
    per = max(0.5, float(duration) / len(sentences))
    lines = []
    for i, s in enumerate(sentences):
        start = i * per
        end = min(duration, (i + 1) * per)
        lines.append(f"{i+1}\n{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n{s}\n")
    out_path.write_text('\n'.join(lines))
    return out_path

# Forced-alignment using aeneas (optional)
def align_with_aeneas(script_text, audio_path, out_srt_path: Path, lang='eng'):
    try:
        from aeneas.executetask import ExecuteTask
        from aeneas.task import Task
        # prepare temp txt
        txt_path = out_srt_path.with_suffix('.txt')
        txt_path.write_text(script_text, encoding='utf-8')
        config_string = f"task_language={lang}|is_text_type=plain|os_task_file_format=srt"
        task = Task(config_string=config_string, text_file=str(txt_path), audio_file=str(audio_path), output_file=str(out_srt_path))
        ExecuteTask(task).execute()
        task.output_sync_map_file()
        # cleanup
        try:
            txt_path.unlink()
        except Exception:
            pass
        return out_srt_path
    except Exception as e:
        print('Aeneas alignment failed or not installed:', e)
        return None

# Optional: YouTube upload helper
def upload_srt_to_youtube(youtube_service, video_id, srt_path, language='en', name='English'):
    from googleapiclient.http import MediaFileUpload
    body = {
        'snippet': {
            'language': language,
            'name': name,
            'videoId': video_id
        }
    }
    media = MediaFileUpload(str(srt_path), mimetype='application/octet-stream')
    resp = youtube_service.captions().insert(part='snippet', body=body, media_body=media).execute()
    return resp
