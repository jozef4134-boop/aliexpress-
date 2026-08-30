import os
import requests
import telebot
import time
import threading
import re
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

# מאגר הדילים והקופונים - שדה image_url הוסר! הבוט יביא את התמונה לבד!
HOT_DEALS_DATABASE = [
    {
        "id": "1005006135439564", 
        "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם, סינון רעשים וסוללה חזקה", 
        "price": 42.0, 
        "discount": 45, 
        "emoji": "🎧",
        "custom_url": None
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
        "id": "page_coupons", 
        "title": "🎁 מרכז הקופונים הרשמי של אלי אקספרס! ככנסו לאסוף קופוני חנות והנחות שוות לפני כולם", 
        "price": 0.0, 
        "discount": 100, 
        "emoji": "🏷️",
        "custom_url": "https://aliexpress.com"
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
        "id": "1005006093849502", 
        "title": "שואב אבק אלחוטי נטען לרכב ולבית בעוצמת שאיבה מטורפת 9000PA", 
        "price": 54.0, 
        "discount": 60, 
        "emoji": "🧹",
        "custom_url": None
    }
]

last_posted_index = 0

def fetch_aliexpress_image(url):
    """פונקציה חכמה שנכנסת לדף באליאקספרס ושולפת את תמונת המוצר הראשית לבד"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # חיפוש תמונות שמסתיימות ב- .jpg מתוך קוד העמוד של אליאקספרס
            images = re.findall(r'https://img\.alicdn\.com/[^\s"\']+\.jpg', response.text)
            if images:
                return images[0] # מחזיר את התמונה הראשונה שנמצאה
    except Exception as e:
        print(f"⚠️ לא הצלחתי לשלוף תמונה אוטומטית: {e}")
    
    # תמונת גיבוי כללית למקרה שאליאקספרס חסמה את הסריקה באותו רגע
    return "https://unsplash.com"

def run_auto_post_cycle():
    """הלולאה האוטומטית שמפרסמת פוסט מעוצב עם תמונה אוטומטית כל 5 דקות"""
    global last_posted_index
    print("🔄 מפעיל סבב פרסום אוטומטי ושולף תמונה לבד...")
    
    item = HOT_DEALS_DATABASE[last_posted_index]
    price = item["price"]
    discount = item["discount"]
    pid = item["id"]
    title = item["title"]
    emoji = item["emoji"]
    custom_url = item.get("custom_url")
    
    last_posted_index = (last_posted_index + 1) % len(HOT_DEALS_DATABASE)
    
    # בניית הקישור הגולמי
    if custom_url:
        raw_link = custom_url
    else:
        raw_link = f"https://aliexpress.com{pid}.html"
    
    # שליפת התמונה באופן אוטומטי מהאתר
    image_url = fetch_aliexpress_image(raw_link)
    
    # הצמדת ה-Tracking ID שלך לקישור
    if "?" in raw_link:
        affiliate_link = f"{raw_link}&sourceType=affiliate&trackingId={TRACKING_ID}"
    else:
        affiliate_link = f"{raw_link}?sourceType=affiliate&trackingId={TRACKING_ID}"
    
    if price > 0:
        price_text = f"<b>מחיר בשקלים:</b> {price:.2f} ש''ח\n"
    else:
        price_text = "<b>מחיר:</b> קופוני הנחה משתנים! 🎁\n"

    # עיצוב הטקסט מתחת לתמונה
    message_text = (
        f"{emoji} <b>דיל חם מעלי אקספרס!</b> {emoji}\n\n"
        f"<b>מוצר:</b> {title}\n"
        f"{price_text}"
        f"<b>אחוז הנחה:</b> {discount}%\n\n"
        f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
        f"{affiliate_link}"
    )
    
    try:
        # שליחת התמונה האוטומטית והטקסט
        bot.send_photo(CHAT_ID, image_url, caption=message_text, parse_mode='HTML')
        print(f"🎯 הצלחה מוחלטת! פוסט עם תמונה אוטומטית שוגר בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בשליחת הודעה: {e}")

def posting_loop():
    """לולאת זמן שרצה ברקע נפרד ומפרסמת כל 5 דקות (300 שניות)"""
    time.sleep(5)
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        time.sleep(300) # השהייה של 300 שניות (5 דקות) בדיוק
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
