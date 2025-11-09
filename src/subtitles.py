from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip
import re, tempfile

def add_subtitles(video_path, narration_text, font_size=55):
    """
    Adds timed subtitles that appear in sync with narration sentences.
    """
    print("📝 Adding subtitles overlay...")

    # Split narration into sentences
    sentences = re.split(r'(?<=[.!?]) +', narration_text.strip())
    clips = []
    duration_per_sentence = 3  # adjust based on video duration

    base = VideoFileClip(video_path)
    t = 0
    for s in sentences:
        txt_clip = (TextClip(s, fontsize=font_size, color='white', bg_color='black')
                    .set_position(("center", "bottom"))
                    .set_duration(duration_per_sentence)
                    .set_start(t))
        clips.append(txt_clip)
        t += duration_per_sentence

    final = CompositeVideoClip([base, *clips])
    out_path = tempfile.mktemp(suffix="_sub.mp4")
    final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac")
    base.close()
    return out_path
