# YouTube Auto Channel - Quick Setup

## 1. Create GitHub repo and add files from this bundle.
## 2. Add the following GitHub Secrets (exact names):
- CLOUDINARY_API_KEY
- COVERR_API_KEY
- ELEVEN_API_KEY
- HF_API_TOKEN
- OPENAI_API_KEY
- PEXELS_API_KEY
- PIXABAY_API_KEY
- REPLICATE_API_TOKEN
- STORYBLOCKS_API_KEY
- VECTEEZY_API_KEY
- YT_CHANNEL_ID
- YT_CLIENT_ID
- YT_CLIENT_SECRET
- YT_REFRESH_TOKEN

(You already have these keys — just paste into repo Settings → Secrets)

## 3. Enable Actions in repo. Workflow .github/workflows/auto_publish.yml triggers daily.
## 4. The runner requires ffmpeg and Python 3.11+. The workflow installs them automatically.
## 5. First run: set TEST_RUN=true in workflow_dispatch or leave default — first run will upload only one test long video.
## 6. Logs and generated assets are under ./workspace/ in the runner and stored in Actions artifacts for debugging.
