# Fully Automated Animal YouTube Channel

## Overview
This is a self-healing, fully automated content factory that runs on GitHub Actions. It produces Long videos and Shorts about animals, handles SEO, and manages community posts.

## Setup
1. Fork this repository.
2. Add the following Secrets in GitHub:
   - `OPENAI_API_KEY`
   - `PEXELS_API_KEY`
   - `YOUTUBE_CREDENTIALS` (JSON)
3. Enable the workflow in `.github/workflows/produce.yml`.

## Architecture
- **Scripts**: Python 3.11 modules in `/scripts`.
- **Config**: JSON files in `/config`.
- **Fallbacks**: Automated switching between OpenAI/Gemini/Wiki and ElevenLabs/gTTS.

## Local Run
```bash
pip install -r requirements.txt
python scripts/pipeline_runner.py
