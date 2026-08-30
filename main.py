import os
import requests
import telebot
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render כדי שלא יקרוס
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

# מאגר הדילים הוויראליים (גאדג'טים, אלקטרוניקה, כלי בית ונעלי גברים)
HOT_DEALS_DATABASE = [
    {"id": "1005006135439564", "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם וסוללה חזקה", "price": 42.0, "discount": 45, "img": "https://alicdn.com"},
    {"id": "1005005822349102", "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים ומחשבים", "price": 98.5, "discount": 35, "img": "https://alicdn.com"},
    {"id": "1005006321948501", "title": "רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף", "price": 145.0, "discount": 42, "img": "https://alicdn.com"},
    {"id": "1005005112349583", "title": "משקפת מקצועית עוצשתית HD לטיולים, שטח וצפייה בכוכבים", "price": 79.0, "discount": 55, "img": "https://alicdn.com"},
    {"id": "1005006093849502", "title": "שואב אבק אלחוטי נטען לרכב ולבית בעוצמת שאיבה מטורפת 9000PA", "price": 54.0, "discount": 60, "img": "https://alicdn.com"},
    {"id": "1005005991827493", "title": "נעלי ריצה וספורט גברים קלות ונושמות בעיצוב אופנתי ונוחות שיא", "price": 139.0, "discount": 48, "img": "https://alicdn.com"},
    {"id": "1005006410294850", "title": "משאבת אוויר חשמלית דיגיטלית ניידת לרכב, קורקינט וכדורים", "price": 112.0, "discount": 38, "img": "https://alicdn.com"},
    {"id": "1005006223401948", "title": "תיק גב חכם חסין מים לגברים עם חיבור USB מובנה לטעינה", "price": 68.0, "discount": 40, "img": "https://alicdn.com"},
    {"id": "1005005510294851", "title": "מכונת תספורת ועיצוב זקן מקצועית לגברים בעיצוב וינטג' מוזהב", "price": 38.0, "discount": 65, "img": "https://alicdn.com"},
    {"id": "1005006123495811", "title": "מעמד סמארטפון מגנטי חזק במיוחד לרכב - מתאים לכל סוגי המכשירים", "price": 19.5, "discount": 70, "img": "https://alicdn.com"}
]

def generate_clean_affiliate_link(product_id):
    return f"https://aliexpress.com{product_id}.html&tracking_id={TRACKING_ID}"

def run_bot_cycle():
    print("🔄 מתחיל סבב פרסום מוצרים מהמאגר...")
    posted_count = 0
    
    for item in HOT_DEALS_DATABASE:
        price = item["price"]
        discount = item["discount"]
        pid = item["id"]
        title = item["title"]
        img = item["img"]
        
        should_post = False
        if price <= 120 and discount >= 25:
            should_post = True
        elif price > 125 and discount >= 40:
            should_post = True
            
        if should_post:
            affiliate_link = generate_clean_affiliate_link(pid)
            
            # טקסט נקי בלי עיצובים מורכבים שיכולים לשבור את טלגרם
            message_text = (
                f"דיל מטורף מעלי אקספרס!\n\n"
                f"מוצר: {title}\n"
                f"מחיר בשקלים: {price:.2f} ש''ח\n"
                f"אחוז הנחה: {discount}%\n\n"
                f"לקנייה ישירה לחצו כאן:\n{affiliate_link}"
            )
            
            try:
                bot.send_photo(CHAT_ID, img, caption=message_text)
                print(f"✅ מוצר {pid} נשלח בהצלחה לערוץ!")
                posted_count += 1
                time.sleep(15)
            except Exception as e:
                print(f"❌ שגיאה בשליחת הודעה: {e}")
                
    if posted_count == 0:
        print("⚠️ לא נמצאו מוצרים שעמדו בתנאי הסינון.")

def main_loop():
    print("🚀 הבוט העוקף פועל כעת בהצלחה ברקע...")
    try:
        run_bot_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        time.sleep(7200)

if __name__ == "__main__":
    main_loop()
