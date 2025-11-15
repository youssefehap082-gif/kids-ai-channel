WildFacts Hub — Production automation

Steps to run:
1. Add all necessary secrets to GitHub repo:
   - OPENAI_API_KEY, ELEVEN_API_KEY, GEMINI_API_KEY (optional), PEXELS_API_KEY, PIXABAY_API_KEY,
     YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CHANNEL_ID, REPLICATE_API_TOKEN, HF_API_TOKEN

2. Populate `data/animal_list.txt` with the animals you want (one per line). If you want me to fetch 1500 real species, tell me and I will fetch them.

3. Ensure you have local assets (assets/videos/) or enable Pexels/Pixabay keys to let the workflow download clips.

4. Trigger Actions -> Daily Upload -> Run workflow (production). The workflow will:
   - Create venv, install dependencies
   - Run `fetch_wikipedia.py` to generate `data/animal_database.json` from your `animal_list.txt`
   - Run `scripts/main.py --mode production` that:
     * On first run: uploads 1 Long + 1 Short as a validation
     * Afterwards: produces 2 Long videos + 6 Shorts per run
