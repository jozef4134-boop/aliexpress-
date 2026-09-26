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
        print(f"Dummy server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. הנתונים המדויקים של הבוט והערוץ שלך
TOKEN = "8810138861:AAFdsv00FYSF8hDrIffvAHA1PY144V61GcA"
CHANNEL_ID = "-1002220456108"

def send_immediate_activation_message():
    print("🔥 מפעיל שליחה מיידית לערוץ טלגרם...")
    
    url = f"https://telegram.org{TOKEN}/sendMessage"
    
    # תוכן ההודעה המיידית
    payload = {
        "chat_id": CHANNEL_ID,
        "text": "📢 הערוץ פעיל רשמית! הבוט מחובר ברקע ועובד.",
        "parse_mode": "HTML"
    }
    
    try:
        # שליחה ישירה ללא המתנה
        response = requests.post(url, json=payload, timeout=10)
        print(f"📡 קוד סטטוס מטלגרם: {response.status_code}")
        print(f"📝 תשובה רשמית משרתי טלגרם: {response.text}")
        
        if response.status_code == 200:
            print("🎯 הצלחה! ההודעה עלתה לערוץ בהצלחה מרובה.")
        else:
            print("⚠️ טלגרם סירבה לקבל את ההודעה. בדוק את השגיאה למעלה.")
            
    except Exception as e:
        print(f"❌ שגיאת תקשורת חמורה מול טלגרם: {e}")

if __name__ == "__main__":
    # הפעלה מיידית ברגע שהקוד נדלק
    send_immediate_activation_message()
    
    # השארת התהליך באוויר
    while True:
        time.sleep(5)
