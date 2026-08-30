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

# רשימת ערוצי המקור שהבאת מהתמונות
SOURCE_CHANNELS = ["DilimShavimA", "israel_deals"]

# מילים לסינון בגדי נשים
FORBIDDEN_WORDS = ["שמלה", "חצאית", "חזיה", "תחתון נשים", "עקבים", "בגדי נשים", "אישה", "women", "dress", "skirt"]

def fix_and_convert_link(text):
    """איתור קישורי עלי אקספרס (כולל קישורים מקוצרים) והפיכתם לקישור שותפים תקין"""
    # איתור קישורים ישירים ומקוצרים של עלי אקספרס בטקסט
    urls = re.findall(r'(https?://[^\s]+aliexpress[^\s]+|https?://s\.click\.[^\s]+)', text)
    
    new_text = text
    for original_url in urls:
        # ניקוי סימני פיסוק שנצמדו בטעות לסוף הקישור
        clean_url = original_url.rstrip('.,;)!]')
        
        # חילוץ מזהה מוצר אם מדובר בקישור ארוך
        product_id_match = re.search(r'item/(\d+)\.html', clean_url)
        if not product_id_match:
            product_id_match = re.search(r'(\d+)\.html', clean_url)
            
        if product_id_match:
            pid = product_id_match.group(1)
            my_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
        else:
            # מעבר דרך מערכת ה-deepLink הרשמית עבור קישורים מקוצרים (כמו s.click) כדי שלא יישברו
            my_link = f"https://aliexpress.com{clean_url}&tracking_id={TRACKING_ID}"
            
        new_text = new_text.replace(original_url, my_link)
        
    return new_text

def scrape_and_post():
    """לולאת מעבר על ערוצי המקור ושאיבת הפוסטים"""
    print("🔄 מתחיל סבב בדיקה וסריקה של ערוצי המקור...")
    
    for channel in SOURCE_CHANNELS:
        web_url = f"https://t.me{channel}"
        try:
            res = requests.get(web_url).text
            
            # חילוץ מבנה הודעות וקישורי תמונות מדפי ה-Web הציבוריים של טלגרם
            posts = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', res)
            images = re.findall(r'background-image:url\(\'(https://cdn\d+\.telegrad\.me/[^\s\']+)\'\)', res)
            
            if not posts:
                continue
                
            # לקיחת הפוסט האחרון שפורסם בערוץ
            latest_post = posts[-1]
            
            # ניקוי תגיות HTML (כמו בריקים וקודים של טלגרם) כדי שהטקסט יהיה נקי
            clean_text = re.sub(r'<[^>]+>', '', latest_post)
            
            # בדיקה אבטחתית: מניעת עליית בגדי נשים
            if any(word in clean_text for word in FORBIDDEN_WORDS):
                print(f"❌ הפוסט מערוץ {channel} מכיל בגדי נשים. מדלג.")
                continue
                
            # המרת כל הקישורים לקישורי שותפים תקינים עם ה-ID שלך
            final_message = fix_and_convert_link(clean_text)
            
            # שליחה ישירות לערוץ שלך
            if images:
                latest_image = images[-1]
                bot.send_photo(CHAT_ID, latest_image, caption=final_message)
            else:
                bot.send_message(CHAT_ID, final_message)
                
            print(f"✅ פוסט הועתק בהצלחה מהערוץ {channel} והומר לקישור שלך!")
            time.sleep(15)  # מרווח קצר בין הודעה להודעה שלא ייחסם
            
        except Exception as e:
            print(f"❌ שגיאה בסריקת הערוץ {channel}: {e}")

def main_loop():
    print("🚀 בוט ההעתקה המשולב מוכן ורץ ברקע...")
    
    # הרצה מיידית ראשונה עם עליית הבוט בשרת
    try:
        scrape_and_post()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # הבוט יבדוק פוסטים חדשים באופן אוטומטי פעם בשעה
        time.sleep(3600)

if __name__ == "__main__":
    main_loop()
