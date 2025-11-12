# YouTube Auto Channel - Quick Setup

1. Create GitHub repo and paste files exactly as provided.
2. Add GitHub Secrets (Settings > Secrets):
   - PEXELS_API_KEY (optional)
   - PIXABAY_API_KEY (optional)
   - YT_CLIENT_ID
   - YT_CLIENT_SECRET
   - YT_REFRESH_TOKEN
3. Ensure Actions are enabled.
4. Run workflow manually (Actions → YouTube Auto Publish → Run workflow) with TEST_RUN = true to create one test long video (unlisted).
5. Check Actions logs and downloaded artifact workspace for generated video and audio.
6. When satisfied set TEST_RUN = false or schedule will perform daily run producing 2 longs + 5 shorts.
