import os
import requests
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי עבור Render למניעת קריסות
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print("Dummy server started")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

def run_auto_post_cycle():
    """שליחת הדיל ישירות לערוץ טלגרם ללא שבירות קוד"""
    print("🔄 מפעיל סבב פרסום בטוח...")
    
    # פרטי הדיל
    title = "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1"
    price_text = "98.50 שקל"
    discount = "35%"
    affiliate_link = "https://aliexpress.com"
    
    message_text = (
        f"💥 דיל חם מעלי אקספרס! 💥\n\n"
        f"מוצר: {title}\n"
        f"מחיר: {price_text}\n"
        f"הנחה: {discount}\n\n"
        f"🛒 לקנייה ישירה לחצו על הקישור:\n"
        f"{affiliate_link}"
    )
    
    # פנייה ישירה ומדויקת ל-API הרשמי של טלגרם
    telegram_url = "https://telegram.org"
    payload = {
        "chat_id": "@DealsIL2026",
        "text": message_text,
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
        time.sleep(300) # פוסט בכל 5 דקות

if __name__ == "__main__":
    main_loop()
