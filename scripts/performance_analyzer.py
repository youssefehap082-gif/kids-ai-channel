import json
from googleapiclient.discovery import build
from utils import load_json, save_json

class PerformanceAnalyzer:
    def __init__(self):
        self.performance_file = "data/performance_data.json"
        self.performance_data = load_json(self.performance_file, {})
        self.youtube = None  # سيتم تهيئته مع YouTube API
    
    def analyze_performance(self):
        """تحليل أداء الفيديوهات"""
        try:
            # الحصول على إحصائيات الفيديوهات
            video_stats = self._get_video_statistics()
            
            # تحليل البيانات
            best_performers = self._identify_best_performers(video_stats)
            trending_topics = self._identify_trending_topics(video_stats)
            
            # تحديث استراتيجية المحتوى
            self._update_content_strategy(best_performers, trending_topics)
            
        except Exception as e:
            print(f"Performance analysis error: {e}")
    
    def _get_video_statistics(self):
        """الحصول على إحصائيات الفيديوهات من YouTube API"""
        # هذا مثال مبسط - تحتاج لتنفيذ مع YouTube Analytics API
        return [
            {
                "video_id": "123",
                "title": "Lion Facts",
                "views": 1000,
                "likes": 100,
                "comments": 50,
                "retention": 65.5
            }
        ]
    
    def _identify_best_performers(self, video_stats):
        """تحديد أفضل الفيديوهات أداءً"""
        best_videos = sorted(video_stats, 
                           key=lambda x: (x['views'], x['retention']), 
                           reverse=True)[:5]
        
        # استخراج الأنماط الناجحة
        successful_patterns = []
        for video in best_videos:
            patterns = {
                "animal": self._extract_animal_from_title(video['title']),
                "retention_rate": video['retention'],
                "engagement_rate": (video['likes'] + video['comments']) / video['views'] * 100
            }
            successful_patterns.append(patterns)
        
        return successful_patterns
    
    def _identify_trending_topics(self, video_stats):
        """تحديد المواضيع الرائجة"""
        # تحليل العناوين والوصف للعثور على كلمات مفتاحية ناجحة
        trending_keywords = {}
        
        for video in video_stats:
            if video['views'] > 500:  # فيديوهات ذات مشاهدات جيدة
                keywords = self._extract_keywords(video['title'] + " " + video.get('description', ''))
                for keyword in keywords:
                    trending_keywords[keyword] = trending_keywords.get(keyword, 0) + video['views']
        
        return sorted(trending_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _update_content_strategy(self, best_performers, trending_topics):
        """تحديث استراتيجية المحتوى بناءً على الأداء"""
        strategy_update = {
            "successful_animals": [p['animal'] for p in best_performers],
            "top_keywords": [t[0] for t in trending_topics],
            "optimal_video_length": self._calculate_optimal_length(best_performers),
            "best_upload_times": self._analyze_best_times(best_performers)
        }
        
        self.performance_data['content_strategy'] = strategy_update
        save_json(self.performance_file, self.performance_data)
    
    def record_upload(self, animal, video_id):
        """تسجيل بيانات الرفع"""
        if 'upload_history' not in self.performance_data:
            self.performance_data['upload_history'] = []
        
        self.performance_data['upload_history'].append({
            "animal": animal,
            "video_id": video_id,
            "upload_time": json.dumps(str(self._get_current_time()))
        })
        
        save_json(self.performance_file, self.performance_data)
    
    def _extract_animal_from_title(self, title):
        """استخراج اسم الحيوان من العنوان"""
        # تنفيذ بسيط - يمكن تطويره باستخدام الذكاء الاصطناعي
        animals = ["Lion", "Tiger", "Elephant", "Giraffe", "Wolf", "Bear"]
        for animal in animals:
            if animal.lower() in title.lower():
                return animal
        return "Unknown"
    
    def _extract_keywords(self, text):
        """استخراج الكلمات المفتاحية من النص"""
        # تنفيذ بسيط لاستخراج الكلمات المفتاحية
        words = text.lower().split()
        return [word for word in words if len(word) > 4]  # كلمات طويلة نسبياً
    
    def _calculate_optimal_length(self, performers):
        """حساب الطول الأمثل للفيديو"""
        if not performers:
            return 300  # 5 دقائق افتراضياً
        
        # تحليل مدة الفيديوهات الأفضل أداءً
        return 300  # قيمة افتراضية
    
    def _analyze_best_times(self, performers):
        """تحليل أفضل أوقات النشر"""
        return ["12:00", "18:00", "20:00"]  # أوقات افتراضية
    
    def _get_current_time(self):
        from datetime import datetime
        return datetime.now()
