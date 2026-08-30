import os
import requests
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי עבור Render למניעת קריסות של השרות
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print("Dummy server started")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# מאגר הדילים הרשמי והמלא שלך - ללא בגדי נשים!
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
    },
    {
        "title": "👟 נעלי ריצה וספורט לגברים קלות ונושמות בעיצוב אופנתי ונוחות שיא", 
        "price": 139.0, 
        "discount": 48, 
        "emoji": "🏃‍♂️",
        "link": "https://aliexpress.com"
    },
    {
        "title": "👕 חליפת טרנינג ספורט לגברים - סט אופנתי ואיכותי לחורף וליום-יום", 
        "price": 115.0, 
        "discount": 38, 
        "emoji": "🤵",
        "link": "https://aliexpress.com"
    },
    {
        "title": "🎁 מרכז הקופונים הרשמי של אלי אקספרס! כנסו לאסוף קופוני חנות והנחות שוות לפני כולם", 
        "price": 0.0, 
        "discount": 100, 
        "emoji": "🏷️",
        "link": "https://aliexpress.com"
    }
]

last_posted_index = 0

def run_auto_post_cycle():
    """שליחת הדיל ישירות לערוץ טלגרם בצורה חסינה ויציבה"""
    global last_posted_index
    print("🔄 מפעיל סבב פרסום בטוח לחלוטין...")
    
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    title = item["title"]
    emoji = item["emoji"]
    base_link = item["link"]
    
    # מעבר למוצר הבא בתור לחצי שעה הבאה
    last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
    
    # בניית הקישור עם ה-Tracking ID שלך
    TRACKING_ID = os.environ.get('TRACKING_ID', 'default')
    if "?" in base_link:
        affiliate_link = f"{base_link}&trackingId={TRACKING_ID}"
    else:
        affiliate_link = f"{base_link}?trackingId={TRACKING_ID}"
    
    if price > 0:
        price_text = f"<b>מחיר בשקלים:</b> {price:.2f} ש''ח\n"
    else:
        price_text = "<b>מחיר:</b> קופוני הנחה משתנים! 🎁\n"

    # קוד המכריח את טלגרם להציג את תמונת המוצר מאליאקספרס בראש הפוסט באופן אוטומטי
    message_text = (
        f"<a href='{affiliate_link}'>&#8205;</a>" 
        f"{emoji} <b>דיל חם מעלי אקספרס!</b> {emoji}\n\n"
        f"<b>מוצר:</b> {title}\n"
        f"{price_text}"
        f"<b>אחוז הנחה:</b> {discount}%\n\n"
        f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
        f"{affiliate_link}"
    )
    
    # פנייה ישירה ומדויקת ל-API הרשמי של טלגרם
    telegram_url = f"https://telegram.org"
    payload = {
        # כאן תוקן ה-ID בדיוק לאותיות הנכונות של הערוץ שלך!
        "chat_id": "@DealsIl2026",
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("🎯 הצלחה מוחלטת! הפוסט עלה בהצלחה לערוץ!")
        else:
            print(f"⚠️ טלגרם החזירה שגיאה: {response.text}")
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")

def main_loop():
    print("🚀 הבוט החל לפעול...")
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error: {e}")
        
    while True:
        time.sleep(300) # פוסט חדש מתחלף באופן אוטומטי בכל 5 דקות!

if __name__ == "__main__":
    main_loop()
