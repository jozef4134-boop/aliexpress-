import os
import requests
import telebot
import time
import threading
import io
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
    """מאגר דילים פנימי קבוע ויציב עם כתובות התמונות המקוריות של עלי אקספרס"""
    return [
        {"id": "1005006135439564", "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם וסוללה חזקה", "price": 42.0, "discount": 45, "img": "https://alicdn.com"},
        {"id": "1005005822349102", "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים ומחשבים", "price": 98.5, "discount": 35, "img": "https://alicdn.com"},
        {"id": "1005006321948501", "title": "רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף", "price": 145.0, "discount": 42, "img": "https://alicdn.com"},
        {"id": "1005005112349583", "title": "משקפת מקצועית עוצמתית HD לטיולים, שטח וצפייה בכוכבים", "price": 79.0, "discount": 55, "img": "https://alicdn.com"},
        {"id": "1005006093849502", "title": "שואב אבק אלחוטי נטען לרכב ולבית בעוצמת שאיבה מטורפת 9000PA", "price": 54.0, "discount": 60, "img": "https://alicdn.com"},
        {"id": "1005005991827493", "title": "נעלי ריצה וספורט גברים קלות ונושמות בעיצוב אופנתי ונוחות שיא", "price": 139.0, "discount": 48, "img": "https://alicdn.com"}
    ]

last_posted_index = 0

def run_auto_post_cycle():
    """הלולאה שמורידה את התמונה כקובץ בינארי ושולחת אותה בצורה חסינה לטלגרם"""
    global last_posted_index
    print("🔄 מתחיל סבב הורדה והזרמה של מוצר מהמאגר...")
    
    deals = get_automated_deals()
    item = deals[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    pid = item["id"]
    title = item["title"]
    img_url = item["img"]
    
    # קידום התור לחצי שעה הבאה
    last_posted_index = (last_posted_index + 1) % len(deals)
    
    if any(word in title for word in FORBIDDEN_WORDS):
        return

    # בניית קישור שותפים תקין ונקי
    affiliate_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
    
    # טקסט מעוצב ב-HTML עם קישור מובנה תקין במילה לחצו כאן לקנייה
    message_text = (
        f"🛍️ <b>דיל חם מעלי אקספרס!</b> 🛍️\n\n"
        f"<b>מוצר:</b> {title}\n"
        f"<b>מחיר בשקלים:</b> {price:.2f} ש''ח\n"
        f"<b>אחוז הנחה:</b> {discount}%\n\n"
        f'🛒 <b><a href="{affiliate_link}">לחצו כאן לקנייה ישירה</a></b>'
    )
    
    try:
        print(f"📥 מוריד את קובץ התמונה מהכתובת לזיכרון של Render...")
        # הורדת הקובץ עצמו מהרשת בצורה מאובטחת
        img_response = requests.get(img_url, timeout=15)
        
        if img_response.status_code == 200:
            # הפיכת התמונה לקובץ בינארי (Bytes) שיוצא ישירות לטלגרם
            photo_file = io.BytesIO(img_response.content)
            photo_file.name = "product.jpg"
            
            # שליחת קובץ התמונה המקורי יחד עם טקסט ה-HTML
            bot.send_photo(CHAT_ID, photo_file, caption=message_text, parse_mode='HTML')
            print(f"✅ הצלחה מטורפת! מוצר {pid} שוגר כקובץ תמונה אמיתי עם קישור HTML לחיץ!")
        else:
            raise Exception("Failed to download image file from server")
            
    except Exception as e:
        print(f"❌ שגיאה בהורדת תמונה, שולח כטקסט גיבוי: {e}")
        try:
            bot.send_message(CHAT_ID, message_text, parse_mode='HTML')
        except Exception as e2:
            print(f"❌ שגיאה סופית: {e2}")

def main_loop():
    print("🚀 בוט הזרמת הקבצים העילית פועל כעת ברקע (כל חצי שעה)...")
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        time.sleep(1800)

if __name__ == "__main__":
    main_loop()
