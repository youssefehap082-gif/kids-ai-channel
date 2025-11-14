# video_classifier.py
# Verifies that downloaded clips contain the target animal using CLIP (HuggingFace transformers).
# Samples frames from each clip and computes similarity between frame embeddings and the text prompt.

import torch
from transformers import CLIPProcessor, CLIPModel
from moviepy.editor import VideoFileClip
from pathlib import Path
import numpy as np

MODEL_NAME = 'openai/clip-vit-base-patch32'  # good general-purpose CLIP

CACHE = Path(__file__).resolve().parent / 'tmp' / 'clip_cache'
CACHE.mkdir(parents=True, exist_ok=True)

_device = 'cuda' if torch.cuda.is_available() else 'cpu'
_model = None
_processor = None

def _load_model():
    global _model, _processor
    if _model is None:
        _model = CLIPModel.from_pretrained(MODEL_NAME).to(_device)
        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)

def sample_frames(video_path, n_frames=6):
    clip = VideoFileClip(str(video_path))
    duration = max(0.5, clip.duration)
    # spread sample times across clip
    times = np.linspace(0.2, max(0.3, duration - 0.2), num=min(n_frames, max(1, int(duration))))
    frames = []
    for t in times:
        try:
            frame = clip.get_frame(float(t))
            frames.append(frame)
        except Exception:
            continue
    try:
        clip.reader.close()
    except Exception:
        pass
    return frames

def score_frames_against_text(frames, text):
    _load_model()
    # CLIP accepts list of images and list of texts
    inputs = _processor(text=[text], images=frames, return_tensors='pt', padding=True).to(_device)
    with torch.no_grad():
        outputs = _model(**inputs)
    image_embeds = outputs.image_embeds
    text_embeds = outputs.text_embeds
    # normalize
    image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
    text_embeds = text_embeds / text_embeds.norm(p=2, dim=-1, keepdim=True)
    sims = (image_embeds @ text_embeds.T).squeeze(-1).cpu().numpy()
    return float(np.mean(sims))

def verify_clip_contains_animal(video_path, animal_name, threshold=0.22):
    """
    Return True if clip likely contains the animal.
    Threshold is conservative; tune after checking CACHE scores.
    """
    try:
        frames = sample_frames(video_path, n_frames=8)
        if not frames:
            return False
        score = score_frames_against_text(frames, animal_name)
        # write debug score
        try:
            (CACHE / (Path(video_path).stem + '.score.txt')).write_text(f"{score}\n")
        except Exception:
            pass
        return float(score) >= float(threshold)
    except Exception as e:
        print('Classifier error', e)
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python video_classifier.py <video_path> <animal_name>")
    else:
        print(verify_clip_contains_animal(sys.argv[1], sys.argv[2]))
