import os
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import resize
from voice_generator import VoiceGenerator
import random

class VideoCreator:
    def __init__(self):
        self.voice_generator = VoiceGenerator()
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        
    def create_long_video(self, content, voice_gender="male"):
        """إنشاء فيديو طويل"""
        try:
            # الحصول على مقاطع فيديو
            video_clips = self._get_video_clips(content['animal'], 5)  # 5 مقاطع
            
            # إنشاء التعليق الصوتي
            voiceover_path = self.voice_generator.generate_voiceover(
                content['script'], voice_gender
            )
            
            # تجميع الفيديو
            final_video = self._assemble_video(video_clips, voiceover_path, content)
            
            # إضافة النهاية مع رسالة الاشتراك
            final_video = self._add_ending(final_video)
            
            output_path = f"outputs/videos/{content['animal']}_{content['is_short']}.mp4"
            final_video.write_videofile(output_path, fps=24)
            
            return output_path
            
        except Exception as e:
            print(f"Video creation error: {e}")
            return self._create_fallback_video(content, voice_gender)
    
    def create_short_video(self, content):
        """إنشاء شورت"""
        try:
            # الحصول على مقاطع فيديو للشورت
            video_clips = self._get_video_clips(content['animal'], 3, vertical=True)
            
            # إضافة موسيقى بدون حقوق
            music_path = self._get_background_music()
            
            # تجميع الشورت
            final_short = self._assemble_short(video_clips, music_path, content)
            
            output_path = f"outputs/shorts/{content['animal']}_short.mp4"
            final_short.write_videofile(output_path, fps=30)
            
            return output_path
            
        except Exception as e:
            print(f"Short creation error: {e}")
            return self._create_fallback_short(content)
    
    def _get_video_clips(self, animal, count, vertical=False):
        """الحصول على مقاطع فيديو من APIs"""
        clips = []
        
        # محاولة Pexels أولاً
        if self.pexels_api_key:
            try:
                pexels_clips = self._download_pexels_videos(animal, count, vertical)
                clips.extend(pexels_clips)
            except Exception as e:
                print(f"Pexels error: {e}")
        
        # إذا لم يكفِ، استخدام Pixabay
        if len(clips) < count and self.pixabay_api_key:
            try:
                pixabay_clips = self._download_pixabay_videos(animal, count - len(clips), vertical)
                clips.extend(pixabay_clips)
            except Exception as e:
                print(f"Pixabay error: {e}")
        
        # إذا لم يوجد مقاطع، استخدام مقاطع افتراضية
        if not clips:
            clips = self._get_fallback_videos(animal, count, vertical)
        
        return clips
    
    def _download_pexels_videos(self, animal, count, vertical=False):
        """تحميل مقاطع من Pexels"""
        orientation = "portrait" if vertical else "landscape"
        url = f"https://api.pexels.com/videos/search?query={animal}&per_page={count}&orientation={orientation}"
        headers = {"Authorization": self.pexels_api_key}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        clips = []
        for video in data.get('videos', [])[:count]:
            video_file = video['video_files'][0]['link']
            # تحميل المقطع (هنا تحتاج لتنفيذ عملية التحميل)
            # clips.append(downloaded_path)
        
        return clips
    
    def _assemble_video(self, video_clips, voiceover_path, content):
        """تجميع الفيديو النهائي"""
        # هذا مثال مبسط - تحتاج لتطوير حسب احتياجاتك
        main_clip = video_clips[0]
        
        # إضافة التعليق الصوتي
        audio_clip = AudioFileClip(voiceover_path)
        video_with_audio = main_clip.set_audio(audio_clip)
        
        # إضافة النصوص (الحقائق)
        text_clips = []
        for i, fact in enumerate(content['facts'][:5]):  # 5 حقائق أولى
            txt_clip = TextClip(fact, fontsize=24, color='white', 
                              stroke_color='black', stroke_width=1)
            txt_clip = txt_clip.set_position(('center', 100 + i*50))
            txt_clip = txt_clip.set_duration(5)  # 5 ثواني لكل حقيقة
            txt_clip = txt_clip.set_start(i*5)  # تبدأ كل 5 ثواني
            text_clips.append(txt_clip)
        
        final_video = CompositeVideoClip([video_with_audio] + text_clips)
        return final_video
    
    def _add_ending(self, video_clip):
        """إضافة نهاية الفيديو مع رسالة الاشتراك"""
        ending_text = TextClip("Don't forget to subscribe and hit the bell for more!", 
                             fontsize=30, color='yellow', stroke_color='black', stroke_width=2)
        ending_text = ending_text.set_position('center').set_duration(5)
        
        final_clip = CompositeVideoClip([video_clip, ending_text.set_start(video_clip.duration-5)])
        return final_clip
    
    def _get_background_music(self):
        """الحصول على موسيقى خلفية"""
        # يمكنك استخدام مكتبات موسيقى مجانية أو APIs
        return "assets/music/background.mp3"  # مسار افتراضي
    
    def _create_fallback_video(self, content, voice_gender):
        """إنشاء فيديو احتياطي إذا فشل الإنشاء"""
        # تنفيذ بسيط للفيديو الاحتياطي
        print("Creating fallback video...")
        return f"outputs/videos/fallback_{content['animal']}.mp4"
    
    def _create_fallback_short(self, content):
        """إنشاء شورت احتياطي"""
        print("Creating fallback short...")
        return f"outputs/shorts/fallback_{content['animal']}_short.mp4"
