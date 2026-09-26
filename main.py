import os
import requests
import time
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started successfully on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# משיכת הנתונים שהגדרת בתוך Render
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8810138861:AAFdsvOOFYSF8hDrIffvAHA1PY144V61GcA')
CHANNEL = os.environ.get('CHAT_ID', '-1002220456108')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

def extract_item_id(url):
    """מחלץ חכם שמנקה את כל הרעש מסביב ומחפש את ה-ID של עלי אקספרס"""
    try:
        # ניקוי הקישור מפרמטרים של חיפוש (כל מה שבא אחרי סימן השאלה) כדי להישאר רק עם כתובת המוצר
        clean_url = url.split('?')[0]
        
        # חיפוש מזהה מוצר רגיל בתוך הכתובת הנקייה
        match = re.search(r'/item/(\d+)', clean_url)
        if match:
            return match.group(1)
            
        # גיבוי: חיפוש רצף מספרים ארוך בתוך הכתובת הנקייה בלבד
        numbers = re.findall(r'(\d{10,20})', clean_url)
        if numbers:
            return numbers[0]
    except Exception as e:
        print(f"Error extracting ID: {e}")
    return None

def send_to_channel(clean_link):
    url = f"https://telegram.org{TOKEN}/sendMessage"
    message_text = (
        f"🛍️ <b>דיל חדש עלה לערוץ!</b> 🛍️\n\n"
        f"🔥 מוצר מומלץ מאלי אקספרס שנמצא עבורכם!\n\n"
        f"🛒 <b>לקנייה ישירה לחצו על הקישור הכחול:</b>\n"
        f"{clean_link}"
    )
    payload = {"chat_id": CHANNEL, "text": message_text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending to channel: {e}")

def check_messages():
    last_id = 0
    url = f"https://telegram.org{TOKEN}/getUpdates"
    print("🚀 הבוט החסין התניע ומקשיב לקישורים שלך...")
    
    while True:
        try:
            payload = {"offset": last_id + 1, "timeout": 30}
            res = requests.get(url, params=payload, timeout=35)
            if res.status_code == 200:
                response = res.json()
                if "result" in response:
                    for update in response["result"]:
                        last_id = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            text = update["message"]["text"]
                            cid = update["message"]["chat"]["id"]
                            
                            # הדפסה ללוגים כדי לוודא בזמן אמת שההודעה התקבלה בשרת
                            print(f"📩 התקבלה הודעה חדשה בצ'אט: {text[:30]}...")
                            
                            if "aliexpress" in text.lower() or "aliex.press" in text.lower():
                                item_id = extract_item_id(text)
                                print(f"🔍 מזהה מוצר שחולץ: {item_id}")
                                
                                if item_id:
                                    aff_link = f"https://aliexpress.com{item_id}.html?trackingId={TRACKING_ID}"
                                    send_to_channel(aff_link)
                                    
                                    requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={
                                        "chat_id": cid, 
                                        "text": "✅ הקישור הומר בהצלחה לקישור שותפים ופורסם בערוץ!"
                                    })
                                else:
                                    requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={
                                        "chat_id": cid, 
                                        "text": "❌ לא הצלחתי לחלץ את מזהה המוצר מהקישור הארוך."
                                    })
            elif res.status_code == 409:
                time.sleep(10)
        except Exception as e:
            time.sleep(5)
        time.sleep(1)

if __name__ == "__main__":
    check_messages()
