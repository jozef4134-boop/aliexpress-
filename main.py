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
    """מנגנון חילוץ חכם במיוחד לכל סוגי הקישורים של עלי אקספרס"""
    # 1. ניסיון חילוץ מקישור ארוך סטנדרטי /item/123456.html
    match = re.search(r'/item/(\d+)\.html', url)
    if match:
        return match.group(1)
        
    # 2. ניסיון חילוץ מקישורים שבהם ה-ID מופיע אחרי סימן שאלה או לוכסן ללא .html
    match_alt = re.search(r'/item/(\d+)', url)
    if match_alt:
        return match_alt.group(1)
        
    # 3. ניסיון אחרון - מציאת רצף המספרים הארוך ביותר בקישור שמתאים ל-ID של מוצר באלי אקספרס
    numbers = re.findall(r'(\d{10,20})', url)
    if numbers:
        return numbers[0] # לוקח את מספר ה-ID הראשון שזוהה
        
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
                            
                            if "aliexpress" in text.lower() or "aliex.press" in text.lower():
                                print(f"📩 קישור התקבל ומעובד כעת...")
                                item_id = extract_item_id(text)
                                
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
                                        "text": "❌ לא הצלחתי לחלץ את מזהה המוצר. נסה לשלוח קישור קצר או נקי יותר."
                                    })
            elif res.status_code == 409:
                time.sleep(10)
        except Exception as e:
            time.sleep(5)
        time.sleep(1)

if __name__ == "__main__":
    check_messages()
