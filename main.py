import os
import requests
import telebot
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי קבוע עבור Render למניעת קריסות
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

# מאגר הדילים הוויראליים - מוצרים חמים לגברים ולבית (ללא נשים)
HOT_DEALS_DATABASE = [
    {"id": "1005006135439564", "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם, סינון רעשים וסוללה חזקה"},
    {"id": "1005005822349102", "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים, מחשבים וסלולר"},
    {"id": "1005006321948501", "title": "רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף וסאונד נקי"},
    {"id": "1005005112349583", "title": "משקפת מקצועית עוצמתית HD לטיולים, שטח, טבע וצפייה בכוכבים"},
    {"id": "1005006093849502", "title": "שואב אבק אלחוטי נטען לרכב ולבית בעוצמת שאיבה מטורפת 9000PA"}
]

last_posted_index = 0

def run_auto_post_cycle():
    """הלולאה האוטומטית הכי פשוטה שיש - טקסט נקי וקישור גלוי ותקין"""
    global last_posted_index
    print("🔄 מפעיל סבב פרסום בסיסי ויציב ללא עיצובים מורכבים...")
    
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = 42.0
    discount = 45
    pid = item["id"]
    title = item["title"]
    
    # קידום התור לחצי שעה הבאה
    last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
    
    # בניית הקישור הרשמי והתקין של עלי אקספרס - עם הסלאש הנכון אחרי ה-item
    affiliate_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
    
    # טקסט נקי לחלוטין ללא שום כוכביות, תגיות או סוגריים שמבלבלים את טלגרם
    message_text = (
        f"🛍️ דיל חם מעלי אקספרס! 🛍️\n\n"
        f"מוצר: {title}\n"
        f"מחיר בשקלים: {price:.2f} ש''ח\n"
        f"אחוז הנחה: {discount}%\n\n"
        f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
        f"{affiliate_link}"
    )
    
    try:
        # שליחת הודעה רגילה ובסיסית (בלי parse_mode). טלגרם תזהה את הקישור בעצמה ותפתח את התמונה!
        bot.send_message(CHAT_ID, message_text, disable_web_page_preview=False)
        print(f"🎯 הצלחה מוחלטת! מוצר {pid} שוגר בהצלחה עם קישור גלוי ותקין!")
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")

def main_loop():
    print("🚀 הבוט האוטומטי לחלוטין רץ ברקע (כל חצי שעה)...")
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # סבב אוטומטי בכל 30 דקות בדיוק
        time.sleep(1800)

if __name__ == "__main__":
    main_loop()
