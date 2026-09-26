import os
import requests
import time
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render כדי שהשירות יישאר באוויר
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started successfully on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# הגדרות המערכת הרשמיות שלך
TELEGRAM_TOKEN = "8810138861:AAFdsvOOFYSF8hDrIffvAHA1PY144V61GcA"
CHANNEL_ID = "-1002220456108"
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

def extract_item_id(url):
    """מחלץ את מזהה המוצר מתוך כל סוג של קישור אלי אקספרס"""
    match = re.search(r'/item/(\d+)\.html', url)
    if match:
        return match.group(1)
    
    # ניסיון נוסף לקישורים קצרים או מובנים אחרת
    numbers = re.findall(r'(\d{10,20})', url)
    if numbers:
        return numbers[0]
        
    return None

def send_to_channel(clean_link):
    """שולח את הדיל המעובד ישירות לערוץ הציבורי שלך"""
    telegram_url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
    message_text = (
        f"🛍️ <b>דיל חדש עלה לערוץ!</b> 🛍️\n\n"
        f"🔥 מוצר מומלץ מאלי אקספרס שנמצא עבורכם!\n\n"
        f"🛒 <b>לקנייה ישירה לחצו על הקישור הכחול:</b>\n"
        f"{clean_link}"
    )
    
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message_text,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(telegram_url, json=payload, timeout=10)
        print(f"תשובת שליחה לערוץ: {res.text}")
    except Exception as e:
        print(f"Error sending to channel: {e}")

def check_messages():
    """לולאה שמקשיבה להודעות שאתה שולח לבוט בפרטי"""
    last_update_id = 0
    telegram_url = f"https://telegram.org{TELEGRAM_TOKEN}/getUpdates"
    
    print("🚀 הבוט מקשיב כעת להודעות שלך בטלגרם...")
    
    while True:
        try:
            payload = {"offset": last_update_id + 1, "timeout": 20}
            response = requests.get(telegram_url, params=payload, timeout=25).json()
            
            if "result" in response:
                for update in response["result"]:
                    last_update_id = update["update_id"]
                    
                    if "message" in update and "text" in update["message"]:
                        user_text = update["message"]["text"]
                        chat_id = update["message"]["chat"]["id"]
                        
                        if "aliexpress" in user_text.lower() or "aliex.press" in user_text.lower():
                            print(f"📩 התקבל קישור לעיבוד: {user_text}")
                            
                            item_id = extract_item_id(user_text)
                            if item_id:
                                affiliate_link = f"https://aliexpress.com{item_id}.html?trackingId={TRACKING_ID}"
                                send_to_channel(affiliate_link)
                                
                                requests.post(f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage", json={
                                    "chat_id": chat_id,
                                    "text": "✅ הקישור הומר בהצלחה לקישור שותפים ופורסם בערוץ!"
                                })
                            else:
                                requests.post(f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage", json={
                                    "chat_id": chat_id,
                                    "text": "❌ לא הצלחתי לחלץ את מזהה המוצר מהקישור."
                                })
        except Exception as e:
            print(f"Error in message loop: {e}")
        time.sleep(2)

if __name__ == "__main__":
    check_messages()
