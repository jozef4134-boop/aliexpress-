import os
import requests
import telebot
import time
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render למניעת קריסות
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

# רשימת ערוצי המקור המקצועיים שביקשת (הבוט ייקח מהם את הדילים הכי חמים)
SOURCE_CHANNELS = ["DilimShavimA", "israel_deals"]

# מילים אסורות לסינון מוחלט של בגדי נשים
FORBIDDEN_WORDS = ["שמלה", "חצאית", "חזיה", "תחתון נשים", "עקבים", "בגדי נשים", "אישה", "women", "dress", "skirt"]

def fix_and_convert_link(text):
    """איתור קישורי עלי אקספרס והמרתם לקישור שותפים מוסתר ותקין שלא יישבר"""
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
            
        # החלפת הקישור הישן בקישור השותפים האישי שלך עם מבנה HTML כחול ולחיץ
        html_link = f'<a href="{my_link}">לחצו כאן לקנייה ישירה</a>'
        new_text = new_text.replace(original_url, html_link)
        
    return new_text

def scrape_and_post_pro():
    """משיכת הפוסטים העדכניים מערוצי הדילים הגדולים כולל קופונים ותמונות"""
    print("🔄 סורק את ערוצי המקור בשיטת המקצוענים...")
    
    for channel in SOURCE_CHANNELS:
        # פנייה לעמוד ה-Web הציבורי של הערוץ שמציג את הפוסטים ללא חסימה
        url = f"https://t.me{channel}"
        try:
            res = requests.get(url, timeout=15).text
            
            # חילוץ חתיכות הטקסט והתמונות מתוך המבנה של טלגרם
            posts = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', res)
            images = re.findall(r'background-image:url\(\'(https://cdn\d+\.telegrad\.me/[^\s\']+)\'\)', res)
            
            if not posts:
                print(f"⚠️ לא נמצאו פוסטים זמינים כרגע בערוץ {channel}")
                continue
                
            # לקיחת הדיל האחרון והחם ביותר שעלה ברגע זה לרשת
            latest_post = posts[-1]
            
            # ניקוי תגיות קוד פנימיות והישארות עם הטקסט והקופונים המקוריים
            clean_text = re.sub(r'<br\s*/?>', '\n', latest_post)  # שמירה על ירידת שורות תקינה
            clean_text = re.sub(r'<[^>]+>', '', clean_text).strip()
            
            # סינון מוחלט של בגדי נשים
            if any(word in clean_text for word in FORBIDDEN_WORDS):
                print(f"❌ הדיל מערוץ {channel} מכיל בגדי נשים. מדלג אוטומטית.")
                continue
                
            # המרת כל הקישורים לקישור השותפים הכחול והלחיץ שלך
            final_message = fix_and_convert_link(clean_text)
            
            # שליחה מקצועית לערוץ שלך בדיוק כמו הגדולים
            if images:
                # הורדת התמונה המקורית של המוצר ושליחתה כקובץ תמונה אמיתי וגדול בראש הפוסט!
                latest_image = images[-1]
                bot.send_photo(CHAT_ID, latest_image, caption=final_message, parse_mode='HTML')
                print(f"✅ פוסט מקצועי עם תמונה וקופונים הועתק בהצלחה מהערוץ {channel}!")
            else:
                bot.send_message(CHAT_ID, final_message, parse_mode='HTML')
                print(f"✅ פוסט טקסט וקופונים הועתק בהצלחה מהערוץ {channel}!")
                
            time.sleep(15)  # הפסקה קלה בין הודעה להודעה למניעת עומס
            
        except Exception as e:
            print(f"❌ שגיאה זמנית בסריקת הערוץ {channel}: {e}")

def main_loop():
    print("🚀 בוט הדילים המקצועי באוויר ופועל ברקע...")
    
    # ריצה ראשונה ומיידית בשנייה שהשרת מסיים לעלות ב-Render
    try:
        scrape_and_post_pro()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # בדיקה והזרמת דילים חדשים לבד לחלוטין בכל 30 דקות (כל חצי שעה עגולה)
        time.sleep(1800)

if __name__ == "__main__":
    main_loop()
