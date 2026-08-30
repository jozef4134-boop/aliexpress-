import os
import requests
import telebot
import time
from datetime import datetime
import pytz
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי עבור Render החינמי
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. הגדרות ומשתני סביבה
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
israel_tz = pytz.timezone('Asia/Jerusalem')

FORBIDDEN_WORDS = ["שמלה", "חצאית", "חזיה", "תחתון נשים", "עקבים", "בגדי נשים", "נשים", "אישה", "women", "dress", "skirt"]

def clean_and_convert_link(original_link):
    """חילוץ מזהה מוצר ובניית קישור שותפים ישיר"""
    try:
        product_id_match = re.search(r'item/(\d+)\.html', original_link)
        if not product_id_match:
            product_id_match = re.search(r'(\d+)\.html', original_link)
            
        if product_id_match:
            pid = product_id_match.group(1)
            return f"https://aliexpress.com{pid}&dl_target_url=https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
        
        return f"https://aliexpress.com{original_link}&tracking_id={TRACKING_ID}"
    except Exception as e:
        print(f"Error converting link: {e}")
        return original_link

def fetch_deals_from_source():
    """משיכת מבצעים חמים מערוץ ציבורי פתוח"""
    source_channel = "AliExpress_Deals_Channel" 
    web_url = f"https://t.me{source_channel}"
    try:
        print("🔄 סורק מוצרים חמים מהרשת...")
        res = requests.get(web_url).text
        raw_links = re.findall(r'href="(https://[^\s"]+aliexpress\.com/[^\s"]+)"', res)
        return list(set(raw_links))[:5]
    except Exception as e:
        print(f"Error scanning source: {e}")
        return []

def run_bot_cycle():
    """בדיקת המוצרים ושליחה לערוץ"""
    links = fetch_deals_from_source()
    if not links:
        print("⚠️ לא נמצאו דילים חדשים כרגע.")
        return

    posted = 0
    for link in links:
        if posted >= 3:
            break
            
        title = "גאדג'ט מבוקש מעלי אקספרס"
        price_in_ils = 74.0  # מוצר לדוגמה מתחת ל-120
        discount_percent = 35
        
        if any(word in title for word in FORBIDDEN_WORDS):
            continue

        my_affiliate_link = clean_and_convert_link(link)
        
        message_text = (
            f"🔥 **דיל חם מהרשת!** 🔥\n\n"
            f"📦 **מוצר:** {title}\n"
            f"💰 **מחיר בשקלים:** {price_in_ils:.2f} ₪\n"
            f"📉 **הנחה:** {discount_percent}%\n\n"
            f"👇 **לקנייה מהירה לחצו כאן:**\n{my_affiliate_link}"
        )
        
        try:
            bot.send_message(CHAT_ID, message_text, parse_mode='Markdown')
            print(f"✅ הודעה נשלחה בהצלחה לערוץ עם ה-Tracking ID: {TRACKING_ID}")
            posted += 1
            time.sleep(5)
        except Exception as e:
            print(f"Error sending to channel: {e}")

def main_loop():
    print("🚀 הבוט החדש פועל כעת ברקע...")
    while True:
        try:
            run_bot_cycle()
        except Exception as e:
            print(f"Error in cycle: {e}")
        
        # הרצה מהירה כל 15 שניות כדי שתראה תוצאות מיידיות בטלגרם
        time.sleep(15)

if __name__ == "__main__":
    main_loop()
