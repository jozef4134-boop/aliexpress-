import os
import requests
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי עבור Render למניעת קריסות של השירות
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print("Dummy server started on port", port)
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# מאגר הדילים הרשמי שלך
HOT_DEALS_DATABASE = [
    {
        "title": "🧰 סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים, מחשבים וסלולר", 
        "price": 98.5, 
        "discount": 35, 
        "emoji": "🛠️",
        "link": "https://aliexpress.com"
    },
    {
        "title": "🔊 רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף וסאונד נקי", 
        "price": 145.0, 
        "discount": 42, 
        "emoji": "🎵",
        "link": "https://aliexpress.com"
    },
    {
        "title": "🔭 משקפת מקצועית עוצמתית HD לטיולים, שטח, טבע וצפייה בכוכבים", 
        "price": 79.0, 
        "discount": 55, 
        "emoji": "🗺️",
        "link": "https://aliexpress.com"
    }
]

last_posted_index = 0

def run_auto_post_cycle():
    global last_posted_index
    print("🔄 מפעיל סבב פרסום בטוח ונקי...")
    
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    title = item["title"]
    emoji = item["emoji"]
    base_link = item["link"]
    
    last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
    
    TRACKING_ID = os.environ.get('TRACKING_ID', 'default')
    if "?" in base_link:
        affiliate_link = f"{base_link}&trackingId={TRACKING_ID}"
    else:
        affiliate_link = f"{base_link}?trackingId={TRACKING_ID}"
    
    if price > 0:
        price_text = f"<b>מחיר בשקלים:</b> {price:.2f} ש''ח\n"
    else:
        price_text = "<b>מחיר:</b> קופוני הנחה משתנים! 🎁\n"

    message_text = (
        f"{emoji} <b>דיל חם מעלי אקספרס!</b> {emoji}\n\n"
        f"<b>מוצר:</b> {title}\n"
        f"{price_text}"
        f"<b>אחוז הנחה:</b> {discount}%\n\n"
        f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
        f"{affiliate_link}"
    )
    
    # שליחת הטוקן בצורה מאובטחת
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8810138861:AAFdsvOOFYSF8hDrIffvAHA1PY144V61GcA')
    
    # תיקון הכתובת הרשמית של ה-API של טלגרם
    telegram_url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": "-1002220456108", # ה-ID המקורי של הערוץ שלך
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("🎯 הצלחה מוחלטת! הפוסט עלה לערוץ בהצלחה!")
        else:
            print(f"⚠️ טלגרם החזירה שגיאה: {response.text}")
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")

def main_loop():
    print("🚀 הבוט החל לפעול בהצלחה ברקע...")
    while True:
        try:
            run_auto_post_cycle()
        except Exception as e:
            print(f"Error in cycle: {e}")
        time.sleep(300) # פרסום בכל 5 דקות

if __name__ == "__main__":
    main_loop()
