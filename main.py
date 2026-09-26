import os
import requests
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי עבור Render
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. נתוני הבוט והערוץ שלך
TOKEN = "8810138861:AAFdsv00FYSF6hDrIffvAHA1PY144V61GcA"
CHANNEL_ID = "-1002220456108"

def test_telegram_connection():
    print("🔍 מתחיל בדיקת קשר ישירה מול טלגרם...")
    time.sleep(5)  # המתנה קלה שהשרת יתייצב
    
    url = f"https://telegram.org{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": "📢 הודעת בדיקה: השרת ב-Render מחובר בהצלחה לערוץ הטלגרם!"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"📡 קוד תגובה מטלגרם: {response.status_code}")
        print(f"📝 תשובת השרת של טלגרם: {response.text}")
    except Exception as e:
        print(f"❌ שגיאת רשת חמורה בניסיון לפנות לטלגרם: {e}")

if __name__ == "__main__":
    test_telegram_connection()
    
    # השארת השרת פתוח בשביל הלוגים
    while True:
        time.sleep(10)
