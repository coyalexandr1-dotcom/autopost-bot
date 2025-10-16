import os
import requests
import json
import schedule
import time
from datetime import datetime
import random
import yt_dlp

USER_TOKEN = os.getenv('USER_TOKEN')
PAGE_NAME = os.getenv('PAGE_NAME')

VIRAL_KEYWORDS = [
    "funny reels", "viral tiktok", "trending reels", 
    "comedy shorts", "meme compilation", "funny moments"
]

def download_viral_reels():
    keyword = random.choice(VIRAL_KEYWORDS)
    print(f"🎯 Поиск вирусных рилсов: {keyword}")
    
    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': 'temp_reel.%(ext)s',
        'quiet': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch10:{keyword} shorts"
            info = ydl.extract_info(search_query, download=False)
            
            if info and 'entries' in info:
                videos = []
                for entry in info['entries']:
                    if entry and entry.get('duration', 0) <= 180:
                        videos.append(entry)
                
                if videos:
                    selected_video = random.choice(videos)
                    video_url = selected_video['webpage_url']
                    
                    print(f"📹 Найдено: {selected_video['title']}")
                    ydl.download([video_url])
                    
                    for ext in ['mp4', 'webm', 'mkv']:
                        filename = f'temp_reel.{ext}'
                        if os.path.exists(filename):
                            return filename, selected_video['title']
            
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
    
    return None, None

def get_page_id_and_token():
    if not USER_TOKEN:
        raise Exception("❌ Токен не найден!")
    
    url = "https://graph.facebook.com/v18.0/me/accounts"
    params = {"access_token": USER_TOKEN, "fields": "id,name,access_token"}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        pages = response.json().get("data", [])
        
        for page in pages:
            if page["name"].strip().lower() == PAGE_NAME.strip().lower():
                print(f"✅ Найдена страница: {page['name']} (ID: {page['id']})")
                return page["id"], page["access_token"]
                
        raise Exception(f"❌ Страница '{PAGE_NAME}' не найдена")
        
    except Exception as e:
        raise Exception(f"❌ Ошибка: {e}")

try:
    PAGE_ID, PAGE_ACCESS_TOKEN = get_page_id_and_token()
    print(f"✅ Система готова! PAGE_ID: {PAGE_ID}")
except Exception as e:
    print(e)
    exit()

def publish_reels_with_sound(post_text, video_file):
    if not video_file or not os.path.exists(video_file):
        return False
    
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/videos"
    
    try:
        with open(video_file, 'rb') as file:
            files = {'source': file}
            data = {
                'title': "Вирусный рилс 🎬",
                'description': post_text,
                'access_token': PAGE_ACCESS_TOKEN,
                'published': 'true'
            }
            
            print("📤 Загрузка рилса...")
            response = requests.post(url, files=files, data=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            if 'id' in result:
                print(f"✅ РИЛС ОПУБЛИКОВАН! ID: {result['id']}")
                os.unlink(video_file)
                return True
            else:
                print(f"❌ Ошибка публикации: {result}")
                
    except Exception as e:
        print(f"❌ Ошибка публикации: {e}")
    
    if os.path.exists(video_file):
        os.unlink(video_file)
    
    return False

def main_job():
    print(f"\n🕐 Запуск в {datetime.now()}")
    
    video_file, video_title = download_viral_reels()
    
    if video_file and video_title:
        post_text = f"🔥 {video_title[:50]}...\n\n#вирусный #тренды #рекомендации"
        
        print(f"🚀 Публикация рилса")
        
        success = publish_reels_with_sound(post_text, video_file)
        
        if success:
            print("✅ Риалс опубликован!")
        else:
            print("❌ Ошибка публикации")
    else:
        print("❌ Не скачался рилс")

if __name__ == "__main__":
    print("🚀 ЗАПУСК СИСТЕМЫ ВИРУСНЫХ РИЛСОВ")
    
    schedule.every(30).minutes.do(main_job)
    
    main_job()
    
    print("⏰ Система работает...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
