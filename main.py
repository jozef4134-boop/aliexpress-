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

# מאגר הדילים והקופונים האוטומטי - מעוצב וללא נשים
HOT_DEALS_DATABASE = [
    {
        "id": "page_coupons", 
        "title": "🎁 מרכז הקופונים הרשמי של אלי אקספרס! כנסו לאסוף קופוני חנות והנחות שוות לפני כולם", 
        "price": 0.0, 
        "discount": 100, 
        "emoji": "🏷️",
        "custom_url": "https://aliexpress.com" # עמוד קופונים כללי
    },
    {
        "id": "1005006135439564", 
        "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם, סינון רעשים וסוללה חזקה", 
        "price": 42.0, 
        "discount": 45, 
        "emoji": "🎧",
        "custom_url": None # מוצר רגיל (יבנה לפי ה-ID)
    },
    {
        "id": "1005005822349102", 
        "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים, מחשבים וסלולר", 
        "price": 98.5, 
        "discount": 35, 
        "emoji": "🧰",
        "custom_url": None
    },
    {
        "id": "page_superdeals", 
        "title": "⚡ עמוד הדילים המטורפים (Super Deals) - הנחות קבועות של מעל 35% על המוצרים הכי פופולריים", 
        "price": 0.0, 
        "discount": 50, 
        "emoji": "🔥",
        "custom_url": "https://aliexpress.com" # עמוד מבצעים כללי
    },
    {
        "id": "1005006321948501", 
        "title": "רמקול בלוטות' אלחוטי חסין מים Anker Soundcore 2 - באס מטורף וסאונד נקי", 
        "price": 145.0, 
        "discount": 42, 
        "emoji": "🔊",
        "custom_url": None
    },
    {
        "id": "1005005112349583", 
        "title": "משקפת מקצועית עוצמתית HD לטיולים, שטח, טבע וצפייה בכוכבים", 
        "price": 79.0, 
        "discount": 55, 
        "emoji": "🔭",
        "custom_url": None
    }
]

last_posted_index = 0

def run_auto_post_cycle():
    """הלולאה האוטומטית שמזהה את סוג הקישור, מדביקה מעקב ומפרסמת"""
    global last_posted_index
    print("🔄 מפעיל סבב פרסום אוטומטי ובניית קישור תקין...")
    
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    pid = item["id"]
    title = item["title"]
    emoji = item["emoji"]
    custom_url = item.get("custom_url")
    
    last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
    
    # מנגנון חכם: אם הגדרנו עמוד קופונים/מבצעים כללי - נשתמש בו. אם לא - נבנה קישור מוצר רגיל
    if custom_url:
        raw_link = custom_url
    else:
        raw_link = f"https://aliexpress.com{pid}.html"
    
    # הבוט מדביק ומצמיד את ה-Tracking ID שלך לסוף הקישור בצורה נורמלית לחלוטין
    if "?" in raw_link:
        affiliate_link = f"{raw_link}&sourceType=affiliate&trackingId={TRACKING_ID}"
    else:
        affiliate_link = f"{raw_link}?sourceType=affiliate&trackingId={TRACKING_ID}"
    
    # בניית הפוסט המעוצב לטלגרם
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
        bot.send_message(CHAT_ID, message_text, parse_mode='HTML')
        print(f"🎯 הצלחה מוחלטת! הפוסט שוגר בהצלחה עם קישור נורמלי פעיל!")
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")

def posting_loop():
    """לולאת זמן שרצה ברקע נפרד ומפרסמת כל 30 דקות"""
    time.sleep(5)
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        time.sleep(1800) # חצי שעה בשניות
        try:
            run_auto_post_cycle()
        except Exception as e:
            print(f"Error in cycle run: {e}")

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
