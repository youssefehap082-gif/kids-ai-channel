name: "Shorts Auto Upload (6x)"

on:
  schedule:
    - cron: "0 */4 * * *"   # تشغيل كل 4 ساعات
  workflow_dispatch:         # للتشغيل اليدوي من زر Run

jobs:
  shorts:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install moviepy gTTS google-api-python-client google-auth google-auth-oauthlib requests pillow

      - name: Run Shorts Script
        env:
          YT_CLIENT_ID: ${{ secrets.YT_CLIENT_ID }}
          YT_CLIENT_SECRET: ${{ secrets.YT_CLIENT_SECRET }}
          YT_REFRESH_TOKEN: ${{ secrets.YT_REFRESH_TOKEN }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
        run: |
          echo "🎥 Running Shorts Script..."
          python src/main_shorts.py
