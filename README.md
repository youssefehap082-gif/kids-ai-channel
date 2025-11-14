# youtube-animal-automation

This repo automates creating wildlife videos (long + shorts) and uploading them to YouTube.

Features:
- Downloads clips from Pexels/Pixabay, verifies animal presence with CLIP.
- Generates 10 facts via OpenAI and TTS via ElevenLabs (with multi-tier failover).
- Assembles videos with moviepy.
- Creates accurate captions using aeneas forced-alignment (if installed) and uploads captions to YouTube.
- AI optimizer collects video stats and recommends top animals.

Instructions:
1. Add the required GitHub secrets (see .github/workflows/daily_upload.yml).
2. Add royalty-free music into assets/music.
3. Push to GitHub and run the Actions workflow. First run is in TEST mode (1 long + 1 short).
