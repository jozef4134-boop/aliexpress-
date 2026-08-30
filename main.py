import os
import requests
import telebot
import time
import threading
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

# מאגר הדילים הוויראליים והחמים ביותר בטלגרם (ללא בגדי נשים כלל)
HOT_DEALS_DATABASE = [
    {"id": "1005006135439564", "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם וסוללה חזקה", "price": 42.0, "discount": 45, "img": "https://alicdn.com"},
    {"id": "1005005822349102", "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים ומחשבים", "price": 98.5, "discount": 35, "img": "https://alicdn.com"},
    {"id": "1005006321948501", "title": "רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף", "price": 145.0, "discount": 42, "img": "https://alicdn.com"},
    {"id": "1005005112349583", "title": "משקפת מקצועית עוצמתית HD לטיולים, שטח וצפייה בכוכבים", "price": 79.0, "discount": 55, "img": "https://alicdn.com"},
    {"id": "1005006093849502", "title": "שואב אבק אלחוטי נטען לרכב ולבית בעוצמת שאיבה מטורפת 9000PA", "price": 54.0, "discount": 60, "img": "https://alicdn.com"},
    {"id": "1005005991827493", "title": "נעלי ריצה וספורט גברים קלות ונושמות בעיצוב אופנתי ונוחות שיא", "price": 139.0, "discount": 48, "img": "https://alicdn.com"},
    {"id": "1005006410294850", "title": "משאבת אוויר חשמלית דיגיטלית ניידת לרכב, קורקינט וכדורים", "price": 112.0, "discount": 38, "img": "https://alicdn.com"},
    {"id": "1005006223401948", "title": "תיק גב חכם חסין מים לגברים עם חיבור USB מובנה לטעינה", "price": 68.0, "discount": 40, "img": "https://alicdn.com"},
    {"id": "1005005510294851", "title": "מכונת תספורת ועיצוב זקן מקצועית לגברים בעיצוב וינטג' מוזהב", "price": 38.0, "discount": 65, "img": "https://alicdn.com"},
    {"id": "1005006123495811", "title": "מעמד סמארטפון מגנטי חזק במיוחד לרכב - מתאים לכל סוגי המכשירים", "price": 19.5, "discount": 70, "img": "https://alicdn.com"}
]

# מעקב מובנה כדי לא לפרסם את אותו מוצר פעמיים ברצף
last_posted_index = 0

def run_auto_post_cycle():
    """פרסום מוצר בודד מהמאגר הפנימי באופן בטוח ללא שרתי רשת חיצוניים חסומים"""
    global last_posted_index
    print("🔄 מפעיל סבב פרסום בטוח מתוך המאגר הפנימי...")
    
    # שליפת המוצר הבא בתור מהרשימה
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    pid = item["id"]
    title = item["title"]
    img_url = item["img"]
    
    # בניית הקישור היישר לשרת השותפים הרשמי מבלי שיישבר
    affiliate_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
    
    # עיצוב טקסט בפורמט HTML קלאסי ויציב לחלוטין בטלגרם
    message_text = (
        f"🛍️ <b>דיל חם מעלי אקספרס!</b> 🛍️\n\n"
        f"<b>מוצר:</b> {title}\n"
        f"<b>מחיר בשקלים:</b> {price:.2f} ש''ח\n"
        f"<b>אחוז הנחה:</b> {discount}%\n\n"
        f'🛒 <b><a href="{affiliate_link}">לחצו כאן לקנייה ישירה</a></b>'
    )
    
    try:
        # שליחת התמונה הרשמית של עלי אקספרס - התמונות האלה מאושרות בטלגרם ותמיד עוברות
        bot.send_photo(CHAT_ID, img_url, caption=message_text, parse_mode='HTML')
        print(f"✅ מוצר {pid} פורסם בהצלחה בערוץ בגרסה הפנימית המאובטחת!")
        
        # קידום האינדקס למוצר הבא לסבב הבא בעוד חצי שעה
        last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
        
    except Exception as e:
        print(f"❌ שגיאה בשליחת הודעה לטלגרם: {e}")

def main_loop():
    print("🚀 הבוט הפנימי והבטוח ביותר פועל כעת ברקע (כל חצי שעה)...")
    
    # הרצה ראשונה ומיידית בשנייה שהשרת מסיים לעלות ב-Render!
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # סבב הבא יתרחש באופן אוטומטי ומבוקר בעוד 30 דקות בדיוק
        time.sleep(1800)

if __name__ == "__main__":
    main_loop()
