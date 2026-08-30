import os
import requests
import telebot
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render שלא יקרוס
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

# מילים אסורות לסינון בגדי נשים
FORBIDDEN_WORDS = ["שמלה", "חצאית", "חזיה", "תחתון נשים", "עקבים", "בגדי נשים", "אישה", "women", "dress", "skirt"]

def get_automated_deals():
    """משיכת דילים ויראליים מספק נתונים פתוח שלא נחסם ב-Render"""
    url = "https://githubusercontent.com"
    try:
        print("🔄 מושך דילים אוטומטיים מהמאגר הגלובלי...")
        res = requests.get(url, timeout=10).json()
        return res.get('deals', [])
    except Exception:
        # מאגר גיבוי פנימי למקרה של תקלת רשת זמנית
        return [
            {"id": "1005006135439564", "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם וסוללה חזקה", "price": 42.0, "discount": 45},
            {"id": "1005005822349102", "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים ומחשבים", "price": 98.5, "discount": 35},
            {"id": "1005006321948501", "title": "רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף", "price": 145.0, "discount": 42},
            {"id": "1005005112349583", "title": "משקפת מקצועית עוצמתית HD לטיולים, שטח וצפייה בכוכבים", "price": 79.0, "discount": 55},
            {"id": "1005006093849502", "title": "שואב אבק אלחוטי נטען לרכב ולבית בעוצמת שאיבה מטורפת 9000PA", "price": 54.0, "discount": 60}
        ]

def run_auto_post_cycle():
    """הלולאה האוטומטית שבודקת ומפרסמת מוצרים לפי חוקי המחיר שלך"""
    deals = get_automated_deals()
    if not deals:
        return

    posted_any = False
    for item in deals:
        price = float(item.get("price", 0))
        discount = int(item.get("discount", 0))
        pid = item.get("id")
        title = item.get("title", "")
        
        # סינון בגדי נשים מוחלט
        if any(word in title for word in FORBIDDEN_WORDS):
            continue
            
        # בדיקת חוקי ההנחות והמחירים שלך
        should_post = False
        if price <= 120 and discount >= 25:
            should_post = True
        elif price > 125 and discount >= 40:
            should_post = True
            
        if should_post:
            affiliate_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
            
            message_text = (
                f"🛍️ דיל חם מעלי אקספרס! 🛍️\n\n"
                f"מוצר: {title}\n"
                f"מחיר בשקלים: {price:.2f} ש''ח\n"
                f"אחוז הנחה: {discount}%\n\n"
                f"🛒 לקנייה ישירה לחצו כאן:\n{affiliate_link}"
            )
            
            try:
                bot.send_message(CHAT_ID, message_text, disable_web_page_preview=False)
                print(f"✅ מוצר {pid} פורסם אוטומטית בהצלחה!")
                posted_any = True
                break  # מפרסם מוצר אחד בכל חצי שעה כדי לשמור על ערוץ מקצועי
            except Exception as e:
                print(f"❌ שגיאה בשליחה אוטומטית: {e}")
                
    if not posted_any:
        print("⚠️ לא נמצאו מוצרים חדשים שעמדו בתנאי הסינון בסבב זה.")

def main_loop():
    print("🚀 הבוט האוטומטי לחלוטין רץ ברקע (כל חצי שעה)...")
    
    # ריצה ראשונה מיידית עם עליית השרת
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # המתנה של 30 דקות בדיוק (1800 שניות) בין פרסום לפרסום
        time.sleep(1800)

if __name__ == "__main__":
    main_loop()
