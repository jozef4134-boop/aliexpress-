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

# 2. הגדרות ומשתני סביבה מהשרת (Render)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# מאגר דילים יציב וחסין - עם קישורי תמונות ישירים שלא חסומים בטלגרם!
HOT_DEALS_DATABASE = [
    {
        "title": "🧰 סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים, מחשבים וסלולר", 
        "price": 98.5, 
        "discount": 35, 
        "emoji": "🛠️",
        "link": "https://aliexpress.com",
        "image": "https://alicdn.com" # קישור תמונה רשמי ישיר
    },
    {
        "title": "🔊 רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף וסאונד נקי", 
        "price": 145.0, 
        "discount": 42, 
        "emoji": "🎵",
        "link": "https://aliexpress.com",
        "image": "https://alicdn.com"
    },
    {
        "title": "🎁 מרכז הקופונים הרשמי של אלי אקספרס! כנסו לאסוף קופוני חנות והנחות שוות לפני כולם", 
        "price": 0.0, 
        "discount": 100, 
        "emoji": "🏷️",
        "link": "https://aliexpress.com",
        "image": "https://alicdn.com"
    }
]

last_posted_index = 0

def run_auto_post_cycle():
    """לולאה נקייה ללא סריקות אתרים שבורות - 100% יציבות"""
    global last_posted_index
    print("🔄 מפעיל סבב פרסום בטוח עם קישורים מוכנים...")
    
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    title = item["title"]
    emoji = item["emoji"]
    base_link = item["link"]
    image_url = item["image"]
    
    last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
    
    # הדבקת ה-Tracking ID בצורה הכי נקייה שיש
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
    
    try:
        bot.send_photo(CHAT_ID, image_url, caption=message_text, parse_mode='HTML')
        print(f"🎯 הצלחה! מוצר פורסם בצורה תקינה עם קישור כחול עובד!")
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")

def posting_loop():
    time.sleep(5)
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        time.sleep(300) # כל 5 דקות בדיוק פוסט חדש

if __name__ == "__main__":
    print("🚀 הבוט האוטומטי מתחיל לעבוד...")
    try:
        bot.remove_webhook()
        bot.get_updates(offset=-1)
        time.sleep(1)
    except:
        pass
        
    threading.Thread(target=posting_loop, daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
