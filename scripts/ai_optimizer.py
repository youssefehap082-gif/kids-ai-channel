import openai
import googleapiclient.discovery

def get_video_stats():
    # استخدم YouTube API لجلب الأرقام: المشاهدات، اللايكات، الكومنتات
    # ارجع داتا تناسب التحليل
    return [
        {"title": "Horse Facts", "views": 12400, "likes": 480, "comments": 122},
        {"title": "Snake Secrets", "views": 9000, "likes": 350, "comments": 80},
        # ...
    ]

def analyze_best_video(stats):
    prompt = "Here are the stats for my animal videos:\n"
    prompt += "\n".join([f"{v['title']} -- Views:{v['views']} Likes:{v['likes']} Comments:{v['comments']}" for v in stats])
    prompt += "\nSuggest which animals/topics I should repeat or make new videos about to increase engagement."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a YouTube optimizer assistant."},
                  {"role": "user", "content": prompt}]
    )
    suggested = response['choices'][0]['message']['content']
    return suggested

def main():
    stats = get_video_stats()
    suggestions = analyze_best_video(stats)
    print("Suggested next topics:", suggestions)

if __name__ == "__main__":
    main()
