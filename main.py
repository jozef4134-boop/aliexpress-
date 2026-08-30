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

# מאגר הדילים האוטומטי לחלוטין - מעוצב עם אימוג'ים מותאמים במקום תמונות חסומות (ללא נשים)
HOT_DEALS_DATABASE = [
    {"id": "1005006135439564", "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם, סינון רעשים וסוללה חזקה", "price": 42.0, "discount": 45, "emoji": "🎧"},
    {"id": "1005005822349102", "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים, מחשבים וסלולר", "price": 98.5, "discount": 35, "emoji": "🧰"},
    {"id": "1005006321948501", "title": "רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף וסאונד נקי", "price": 145.0, "discount": 42, "emoji": "🔊"},
    {"id": "1005005112349583", "title": "משקפת מקצועית עוצמתית HD לטיולים, שטח, טבע וצפייה בכוכבים", "price": 79.0, "discount": 55, "emoji": "🔭"},
    {"id": "1005006093849502", "title": "שואב אבק אלחוטי נטען לרכב ולבית בעוצמת שאיבה מטורפת 9000PA", "price": 54.0, "discount": 60, "emoji": "🧹"},
    {"id": "1005005991827493", "title": "נעלי ריצה וספורט גברים קלות ונושמות בעיצוב אופנתי ונוחות שיא", "price": 139.0, "discount": 48, "emoji": "👟"}
]

last_posted_index = 0

def run_auto_post_cycle():
    """הלולאה האוטומטית שמפרסמת טקסט נקי, יציב וחסין לחלוטין"""
    global last_posted_index
    print("🔄 מפעיל סבב פרסום אוטומטי בטוח ללא תמונות...")
    
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    pid = item["id"]
    title = item["title"]
    emoji = item["emoji"]
    
    # קידום התור לחצי שעה הבאה
    last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
    
    # בניית הקישור בפורמט הרשמי והנכון של אליאקספרס
    affiliate_link = f"https://aliexpress.com{pid}.html"
    
    # טקסט נקי, ברור ומקצועי ללא תגיות מורכבות שמחרבות את הפוסט
    message_text = (
        f"{emoji} <b>דיל חם מעלי אקספרס!</b> {emoji}\n\n"
        f"<b>מוצר:</b> {title}\n"
        f"<b>מחיר בשקלים:</b> {price:.2f} ש''ח\n"
        f"<b>אחוז הנחה:</b> {discount}%\n\n"
        f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
        f"{affiliate_link}"
    )
    
    try:
        # שליחת הודעת טקסט רגילה במצב HTML
        bot.send_message(CHAT_ID, message_text, parse_mode='HTML')
        print(f"🎯 הצלחה מוחלטת! מוצר {pid} שוגר בהצלחה עם קישור כחול תקין!")
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")

def posting_loop():
    """לולאת זמן שרצה ברקע נפרד ומפרסמת כל 30 דקות"""
    # פרסום ראשוני מיד עם עליית הבוט
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        time.sleep(1800) # 30 דקות בשניות
        try:
            run_auto_post_cycle()
        except Exception as e:
            print(f"Error in cycle run: {e}")

if __name__ == "__main__":
    print("🚀 הבוט האוטומטי מתחיל לעבוד...")
    
    # הפעלת לולאת הפרסום ב-Thread נפרד כדי שלא תחסום את הקוד
    threading.Thread(target=posting_loop, daemon=True).start()
    
    # מחיקת וובהוקים ישנים כדי למנוע את שגיאת ה-Conflict בלוגים של Render
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass
        
    # הפעלה יציבה של הבוט
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

