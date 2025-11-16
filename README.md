# youtube-animal-automation

Automated YouTube channel pipeline to publish daily animal videos.

## Quick start
1. Add secrets in GitHub repo: OPENAI_API_KEY, ELEVEN_API_KEY, GEMINI_API_KEY, PEXELS_API_KEY, PIXABAY_API_KEY, REPLICATE_API_TOKEN, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CHANNEL_ID.
2. Populate `data/animal_list.txt` (one species per line). Optionally add a large list (1500).
3. Confirm `.github/workflows/daily_upload.yml` present.
4. Push to `main` and run workflow manually (first run is TEST by default - set TEST_RUN secret to "true"/"false" accordingly).
