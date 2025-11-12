# 🦁 Auto YouTube Animal Channel System

This project automates a YouTube channel about animals using AI—creating, publishing, and optimizing daily animal videos (long & shorts) with automatic SEO, multi-language subtitles, error detection, and performance analysis.  
**Language:** All content is English; subtitles auto-generated for multiple languages.  
**Target:** Non-Arabic foreign audience—faster monetization.

## Workflow
- **GitHub Actions** triggers daily:
    - `generate_long_video.py`: 2 long videos (voiceover, facts, music, subscribe prompt)
    - `generate_short.py`: 5 shorts (music only, no voice)
    - `upload_to_youtube.py`: uploads + SEO metadata + multi-language subs
    - `ai_optimizer.py`: analyzes engagement, suggests next topics for growth

## Secrets to setup (in GitHub repo):
```env
CLOUDINARY_API_KEY
COVERR_API_KEY
ELEVEN_API_KEY
HF_API_TOKEN
OPENAI_API_KEY
PEXELS_API_KEY
PIXABAY_API_KEY
REPLICATE_API_TOKEN
STORYBLOCKS_API_KEY
VECTEEZY_API_KEY
YT_CHANNEL_ID
YT_CLIENT_ID
YT_CLIENT_SECRET
YT_REFRESH_TOKEN
```
## First-time/Test run
- Use `workflow_dispatch` to manually trigger a one-off test (creates one long + one short).

## Main tips
- Everything auto (SEO, tags, translation, upload, error log, AI analytics)
- Subtitle languages: EN, ES, FR, DE, ... etc.
- Music is copyright-free!
- If error in upload, it’s logged and flagged to avoid counting video as “successful”.

Feel free to add more animals in `animals_list.json` and customize the scripts!
