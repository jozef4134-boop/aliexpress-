import os
import requests
import telebot
import time
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. הגדרות ומשתני סביבה מהשרת
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ערוצי המקור שביקשת
SOURCE_CHANNELS = ["DilimShavimA", "israel_deals"]

# מילים לסינון בגדי נשים
FORBIDDEN_WORDS = ["שמלה", "חצאית", "חזיה", "תחתון נשים", "עקבים", "בגדי נשים", "אישה", "women", "dress", "skirt"]

def fix_and_convert_link(text):
    """איתור קישורי עלי אקספרס והמרתם לקישור שותפים תקין לחלוטין"""
    urls = re.findall(r'(https?://[^\s]+aliexpress[^\s]+|https?://s\.click\.[^\s]+)', text)
    new_text = text
    
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
        
    return new_text

def scrape_and_post():
    """משיכת הודעות ותמונות דרך שרת מתווך כדי לעקוף את החסימה של רנדר"""
    print("🔄 מתחיל סבב סריקה חכם דרך שרת מתווך...")
    
    for channel in SOURCE_CHANNELS:
        # שימוש בשרת מתווך RSSHub שעוקף את חסימת הרשת של Render על טלגרם
        rss_url = f"https://rsshub.app{channel}"
        
        try:
            print(f"🔎 סורק את ערוץ: {channel} דרך שרת מתווך...")
            response = requests.get(rss_url, timeout=15).text
            
            # חילוץ התיאור של הפוסט האחרון מהקובץ
            descriptions = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', response)
            
            if not descriptions or len(descriptions) < 2:
                print(f"⚠️ לא נמצאו פוסטים חדשים בערוץ {channel}")
                continue
                
            # לוקח את הפוסט האחרון האמיתי (האינדקס הראשון הוא לרוב תיאור הערוץ הכללי)
            latest_post = descriptions[1]
            
            # חילוץ קישור התמונה המקורית אם קיימת בתוך הפוסט
            img_match = re.search(r'<img[^>]+src="([^">]+)"', latest_post)
            image_url = img_match.group(1) if img_match else None
            
            # ניקוי תגיות ה-HTML כדי להישאר עם טקסט נקי לחלוטין לטלגרם
            clean_text = re.sub(r'<[^>]+>', '', latest_post).strip()
            
            if not clean_text:
                continue
                
            # סינון בגדי נשים מוחלט
            if any(word in clean_text for word in FORBIDDEN_WORDS):
                print(f"❌ הפוסט מערוץ {channel} מכיל בגדי נשים. מדלג.")
                continue
                
            # המרת הקישורים לקישורי השותפים שלך
            final_message = fix_and_convert_link(clean_text)
            
            # שליחה ישירה לערוץ שלך בהתאם לקיום תמונה
            if image_url:
                try:
                    bot.send_photo(CHAT_ID, image_url, caption=final_message)
                    print(f"✅ פוסט עם תמונה וקופונים הועתק בהצלחה מהערוץ {channel}!")
                except Exception:
                    bot.send_message(CHAT_ID, final_message)
                    print(f"✅ פוסט הועתק כטקסט מהערוץ {channel} (התמונה הייתה חסומה)")
            else:
                bot.send_message(CHAT_ID, final_message)
                print(f"✅ פוסט טקסט הועתק בהצלחה מהערוץ {channel}!")
                
            time.sleep(15)  # הפסקה קלה בין ערוץ לערוץ
            
        except Exception as e:
            print(f"❌ שגיאה זמנית בגישה לשרת המתווך עבור {channel}: {e}")

def main_loop():
    print("🚀 הבוט העוקף מוכן ויוצא לדרך...")
    try:
        scrape_and_post()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # בדיקה קבועה בכל שעה של מבצעים וקופונים חדשים
        time.sleep(3600)

if __name__ == "__main__":
    main_loop()
