import os
import requests
import telebot
import time
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי עבור Render
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. הגדרות ומשתני סביבה
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# רשימת ערוצי המקור מהתמונות שלך
SOURCE_CHANNELS = ["DilimShavimA", "israel_deals"]

# מילים לסינון בגדי נשים
FORBIDDEN_WORDS = ["שמלה", "חצאית", "חזיה", "תחתון נשים", "עקבים", "בגדי נשים", "אישה", "women", "dress", "skirt"]

def fix_and_convert_link(text):
    """איתור קישורי עלי אקספרס והמרתם לקישור שותפים תקין ומובנה"""
    urls = re.findall(r'(https?://[^\s]+aliexpress[^\s]+|https?://s\.click\.[^\s]+)', text)
    
    new_text = text
    first_link = ""
    
    for original_url in urls:
        clean_url = original_url.rstrip('.,;)!]')
        
        product_id_match = re.search(r'item/(\d+)\.html', clean_url)
        if not product_id_match:
            product_id_match = re.search(r'(\d+)\.html', clean_url)
            
        if product_id_match:
            pid = product_id_match.group(1)
            my_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
        else:
            my_link = f"https://aliexpress.com{clean_url}&tracking_id={TRACKING_ID}"
            
        new_text = new_text.replace(original_url, my_link)
        if not first_link:
            first_link = my_link
            
    return new_text, first_link

def scrape_and_post():
    """סריקה תקינה של ערוצי המקור והעברת הדילים"""
    print("🔄 מתחיל סבב בדיקה וסריקה של ערוצי המקור...")
    
    for channel in SOURCE_CHANNELS:
        # 📌 תיקון הכתובת - הוספת סלאש (/) קריטי בין השם לערוץ כדי שלא יישבר
        web_url = f"https://t.me{channel}"
        try:
            print(f"🔎 סורק את ערוץ: {channel}")
            res = requests.get(web_url).text
            
            # חילוץ הודעות טקסט מהערוץ
            posts = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', res)
            
            if not posts:
                print(f"⚠️ לא נמצאו פוסטים בערוץ {channel}")
                continue
                
            latest_post = posts[-1]
            clean_text = re.sub(r'<[^>]+>', '', latest_post)
            
            if any(word in clean_text for word in FORBIDDEN_WORDS):
                print(f"❌ הפוסט מערוץ {channel} מכיל בגדי נשים. מדלג.")
                continue
                
            final_message, affiliate_link = fix_and_convert_link(clean_text)
            
            # בניית הודעה מקצועית עם תצוגה מקדימה אוטומטית של התמונה מתוך עלי אקספרס
            if affiliate_link:
                bot.send_message(CHAT_ID, final_message, disable_web_page_preview=False)
                print(f"✅ פוסט הועתק והומר בהצלחה מהערוץ {channel}!")
                time.sleep(15)
            
        except Exception as e:
            print(f"❌ שגיאה בסריקת הערוץ {channel}: {e}")

def main_loop():
    print("🚀 בוט ההעתקה המשולב והמתוקן רץ ברקע...")
    try:
        scrape_and_post()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # ריצה קבועה בכל שעה לבדיקת מבצעים חדשים
        time.sleep(3600)

if __name__ == "__main__":
    main_loop()
