import os
import logging
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import resize
import cv2
import numpy as np

from voice_generator import VoiceGenerator

class VideoCreator:
    def __init__(self):
        self.voice_generator = VoiceGenerator()
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        
    def create_long_video(self, content, voice_gender="male"):
        """إنشاء فيديو طويل مع تعليق صوتي"""
        try:
            logging.info(f"🎬 بدء إنشاء فيديو طويل عن: {content['animal']}")
            
            # الحصول على مقاطع فيديو
            video_clips = self._get_video_clips(content['animal'], duration_needed=60)  # 60 ثانية
            
            if not video_clips:
                logging.error("❌ لا توجد مقاطع فيديو متاحة")
                return None
            
            # إنشاء التعليق الصوتي
            voiceover_path = self.voice_generator.generate_voiceover(
                content['script'], 
                voice_gender=voice_gender
            )
            
            if not voiceover_path or not os.path.exists(voiceover_path):
                logging.error("❌ فشل إنشاء التعليق الصوتي")
                return None
            
            # تجميع الفيديو النهائي
            final_video = self._assemble_long_video(video_clips, voiceover_path, content)
            
            output_path = f"outputs/videos/{content['animal'].lower()}_long_{os.urandom(4).hex()}.mp4"
            
            # حفظ الفيديو النهائي
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            logging.info(f"✅ تم إنشاء الفيديو الطويل: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الفيديو الطويل: {e}")
            return None
    
    def create_short_video(self, content):
        """إنشاء شورت مع موسيقى فقط"""
        try:
            logging.info(f"🎬 بدء إنشاء شورت عن: {content['animal']}")
            
            # الحصول على مقاطع فيديو عمودية للشورت
            video_clips = self._get_video_clips(content['animal'], duration_needed=30, vertical=True)
            
            if not video_clips:
                logging.error("❌ لا توجد مقاطع فيديو متاحة للشورت")
                return None
            
            # الحصول على موسيقى خلفية
            music_path = self._get_background_music()
            
            # تجميع الشورت النهائي
            final_short = self._assemble_short_video(video_clips, music_path, content)
            
            output_path = f"outputs/shorts/{content['animal'].lower()}_short_{os.urandom(4).hex()}.mp4"
            
            # حفظ الشورت النهائي
            final_short.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            logging.info(f"✅ تم إنشاء الشورت: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الشورت: {e}")
            return None
    
    def _get_video_clips(self, animal, duration_needed=60, vertical=False):
        """الحصول على مقاطع فيديو من APIs"""
        clips = []
        total_duration = 0
        
        # محاولة Pexels أولاً
        if self.pexels_api_key:
            try:
                pexels_clips = self._download_pexels_videos(animal, duration_needed, vertical)
                clips.extend(pexels_clips)
                total_duration = sum(clip.duration for clip in clips)
            except Exception as e:
                logging.warning(f"Pexels غير متوفر: {e}")
        
        # إذا لم يكفِ، استخدام Pixabay
        if total_duration < duration_needed and self.pixabay_api_key:
            try:
                pixabay_clips = self._download_pixabay_videos(animal, duration_needed - total_duration, vertical)
                clips.extend(pixabay_clips)
            except Exception as e:
                logging.warning(f"Pixabay غير متوفر: {e}")
        
        if not clips:
            logging.warning("⚠️ استخدام مقاطع افتراضية")
            clips = self._get_fallback_videos(animal, duration_needed, vertical)
        
        return clips
    
    def _download_pexels_videos(self, animal, duration_needed, vertical=False):
        """تحميل مقاطع من Pexels"""
        clips = []
        try:
            orientation = "portrait" if vertical else "landscape"
            url = f"https://api.pexels.com/videos/search?query={animal}+wildlife&per_page=5&orientation={orientation}"
            headers = {"Authorization": self.pexels_api_key}
            
            response = requests.get(url, headers=headers)
            data = response.json()
            
            for video in data.get('videos', [])[:3]:
                video_file = video['video_files'][0]['link']
                # هنا سيتم تنزيل المقطع وتحميله باستخدام moviepy
                # clip = VideoFileClip(video_file)
                # clips.append(clip)
                
        except Exception as e:
            logging.error(f"خطأ في Pexels: {e}")
        
        return clips
    
    def _download_pixabay_videos(self, animal, duration_needed, vertical=False):
        """تحميل مقاطع من Pixabay"""
        clips = []
        try:
            orientation = "vertical" if vertical else "horizontal"
            url = f"https://pixabay.com/api/videos/?key={self.pixabay_api_key}&q={animal}+nature&orientation={orientation}&per_page=5"
            
            response = requests.get(url)
            data = response.json()
            
            for video in data.get('hits', [])[:3]:
                video_url = video['videos']['large']['url']
                # clip = VideoFileClip(video_url)
                # clips.append(clip)
                
        except Exception as e:
            logging.error(f"خطأ في Pixabay: {e}")
        
        return clips
    
    def _assemble_long_video(self, video_clips, voiceover_path, content):
        """تجميع الفيديو الطويل النهائي"""
        try:
            # استخدام المقطع الأول كقاعدة
            main_clip = video_clips[0]
            
            # تحميل التعليق الصوتي
            voiceover = AudioFileClip(voiceover_path)
            
            # ضبط مدة الفيديو مع الصوت
            if main_clip.duration > voiceover.duration:
                main_clip = main_clip.subclip(0, voiceover.duration)
            else:
                # إذا كان الفيديو أقصر، نكرر بعض المقاطع
                pass
            
            # إضافة التعليق الصوتي
            video_with_audio = main_clip.set_audio(voiceover)
            
            # إضافة نصوص الحقائق
            text_clips = []
            facts = content['facts'][:5]  # أول 5 حقائق
            
            for i, fact in enumerate(facts):
                # إنشاء نص لكل حقيقة
                text = TextClip(
                    fact,
                    fontsize=28,
                    color='white',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2
                )
                
                text = text.set_position(('center', 150 + i*80))
                text = text.set_duration(voiceover.duration / len(facts))
                text = text.set_start(i * (voiceover.duration / len(facts)))
                
                text_clips.append(text)
            
            # تجميع الفيديو النهائي
            final_video = CompositeVideoClip([video_with_audio] + text_clips)
            
            return final_video
            
        except Exception as e:
            logging.error(f"خطأ في تجميع الفيديو: {e}")
            raise
    
    def _assemble_short_video(self, video_clips, music_path, content):
        """تجميع الشورت النهائي"""
        try:
            # استخدام المقطع الأول للشورت
            main_clip = video_clips[0]
            
            # تحميل الموسيقى
            music = AudioFileClip(music_path)
            
            # ضبط مدة الشورت (15-60 ثانية)
            target_duration = min(60, max(15, main_clip.duration))
            main_clip = main_clip.subclip(0, target_duration)
            music = music.subclip(0, target_duration)
            
            # إضافة الموسيقى
            video_with_music = main_clip.set_audio(music)
            
            # إضافة نص الحيوان
            animal_text = TextClip(
                content['animal'],
                fontsize=48,
                color='yellow',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3
            )
            
            animal_text = animal_text.set_position(('center', 100))
            animal_text = animal_text.set_duration(target_duration)
            
            # تجميع الشورت النهائي
            final_short = CompositeVideoClip([video_with_music, animal_text])
            
            return final_short
            
        except Exception as e:
            logging.error(f"خطأ في تجميع الشورت: {e}")
            raise
    
    def _get_background_music(self):
        """الحصول على موسيقى خلفية"""
        # يمكنك إضافة مسارات موسيقى مجانية هنا
        return "assets/music/background.mp3"  # يحتاج لملف حقيقي
    
    def _get_fallback_videos(self, animal, duration_needed, vertical=False):
        """مقاطع فيديو افتراضية للاختبار"""
        # في الإصدار الحقيقي، سيتم إنشاء مقاطع افتراضية أو استخدام مكتبة
        return []
