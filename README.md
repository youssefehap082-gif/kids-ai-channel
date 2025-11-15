# Run checklist — Production upload

1. تأكد من إضافة الملفات أعلاه في نفس شجرة المشروع.
2. أضف Secrets في GitHub repo -> Settings -> Secrets and variables -> Actions:
   - PEXELS_API_KEY
   - PIXABAY_API_KEY
   - ELEVEN_API_KEY
   - OPENAI_API_KEY (optional)
   - YT_CLIENT_ID
   - YT_CLIENT_SECRET
   - YT_REFRESH_TOKEN
   - YT_CHANNEL_ID
3. للتأكد محلياً: شغّل:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 scripts/main.py --publish-mode test
   (يجب أن يرفع 1 long + 1 short إذا كانت المفاتيح صحيحة)
4. لإعداد GitHub:
   - Commit كل الملفات
   - Push إلى main
   - اذهب إلى Actions -> Daily Upload -> Run workflow
   - راقب الـ logs؛ أي خطأ انسخه وأرسله لي وسأصلحه فوراً.
5. ملاحظة هامة: YouTube uploader يتطلب `YT_REFRESH_TOKEN` صالح; بدونها لن يتم الرفع الفعلي.
