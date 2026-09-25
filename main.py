import os
import requests
import time
import threading
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render כדי שהשרות יישאר באוויר בחינם
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started successfully on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. מאגר מוצרים אמיתי, מגוון וגדול (ללא בגדי נשים) - הבוט בוחר מפה אוטומטית
HOT_PRODUCTS_POOL = [
    {"title": "🧰 סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1", "id": "1005006135439564", "price": 98.50, "discount": 35, "emoji": "🛠️"},
    {"title": "🔊 רמקול בלוטות' אלחוטי Anker Soundcore 2 חסין מים", "id": "1005005844231902", "price": 145.00, "discount": 42, "emoji": "🎵"},
    {"title": "🔋 מטען קיר מהיר Baseus 65W GaN עם 3 יציאות מהירות", "id": "1005006012448512", "price": 89.00, "discount": 50, "emoji": "🔌"},
    {"title": "🎧 אוזניות אלחוטיות Lenovo LP40 Pro סאונד נקי ומקורי", "id": "1005006135439564", "price": 42.00, "discount": 45, "emoji": "🎧"},
    {"title": "🚗 קומפרסור / משאבת אוויר דיגיטלית ניידת לרכב Xiaomi", "id": "1005005234112904", "price": 129.00, "discount": 38, "emoji": "🚘"},
    {"title": "🧹 שואב אבק ידני אלחוטי עוצמתי לרכב ולבית", "id": "1005005991245871", "price": 65.00, "discount": 60, "emoji": "✨"},
    {"title": "⌚ שעון חכם Xiaomi Mi Band 8 מסך אמולד איכותי", "id": "1005005521443690", "price": 139.00, "discount": 30, "emoji": "⌚"},
    {"title": "🎮 קונסולת משחקי רטרו ניידת עם אלפי משחקים מובנים", "id": "1005005321456981", "price": 75.00, "discount": 52, "emoji": "🕹️"},
    {"title": "🔦 פנס יד טקטי עוצמתי לטווח רחוק חסין מים", "id": "1005005112458796", "price": 49.00, "discount": 40, "emoji": "🔦"},
    {"title": "🐭 עכבר אלחוטי ארגונומי שקט למחשב Logi", "id": "1005005662145893", "price": 85.00, "discount": 33, "emoji": "🖱️"}
]

last_posted_id = None

def run_auto_affiliate_cycle():
    global last_posted_id
    print("🔄 הבוט בוחר מוצר ומייצר קישור שותפים...")
    
    # מניעת חזרה על אותו מוצר ברצף
    available_products = [p for p in HOT_PRODUCTS_POOL if p["id"] != last_posted_id]
    if not available_products:
        available_products = HOT_PRODUCTS_POOL
        
    chosen_item = random.choice(available_products)
    last_posted_id = chosen_item["id"]
    
    # משיכת הנתונים מהשרת (או שימוש בברירות המחדל הקשיחות שלך)
    TRACKING_ID = os.environ.get('TRACKING_ID', 'default')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8810138861:AAFdsvOOFYSF8hDrIffvAHA1PY144V61GcA')
    
    # בניית קישור המוכרים האוטומטי (Affiliate Link)
    affiliate_link = f"https://aliexpress.com{chosen_item['id']}.html?trackingId={TRACKING_ID}"
    
    # עיצוב הפוסט הסופי לערוץ
    message_text = (
        f"{chosen_item['emoji']} <b>דיל חם מעלי אקספרס!</b> {chosen_item['emoji']}\n\n"
        f"<b>מוצר:</b> {chosen_item['title']}\n"
        f"<b>מחיר בשקלים:</b> {chosen_item['price']:.2f} ש''ח\n"
        f"<b>אחוז הנחה:</b> {chosen_item['discount']}%\n\n"
        f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
        f"{affiliate_link}"
    )
    
    # הכתובת המתוקנת והרשמית של טלגרם
    telegram_url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": "-1002220456108",
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"🎯 הצלחה מוחלטת! המוצר {chosen_item['title']} פורסם בהצלחה בערוץ.")
        else:
            print(f"⚠️ טלגרם החזירה שגיאה: {response.text}")
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")

def main_loop():
    print("🚀 הבוט החל לפעול באופן אוטומטי לחלוטין ברקע!")
    while True:
        try:
            run_auto_affiliate_cycle()
        except Exception as e:
            print(f"שגיאה במחזור הריצה: {e}")
        
        # זמן פרסום: בכל 15 דקות (900 שניות) פוסט חדש עולה לבד לערוץ
        time.sleep(900)

if __name__ == "__main__":
    main_loop()
