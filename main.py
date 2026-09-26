import os
import requests
import time
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started successfully on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8810138861:AAFdsvOOFYSF8hDrIffvAHA1PY144V61GcA')
CHANNEL = os.environ.get('CHAT_ID', '-1002220456108')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

def extract_item_id(url):
    match = re.search(r'/item/(\d+)\.html', url)
    if match:
        return match.group(1)
    numbers = re.findall(r'(\d{10,20})', url)
    if numbers:
        return numbers[0]
    return None

def send_to_channel(clean_link):
    url = f"https://telegram.org{TOKEN}/sendMessage"
    message_text = (
        f"🛍️ <b>דיל חדש עלה לערוץ!</b> 🛍️\n\n"
        f"🔥 מוצר מומלץ מאלי אקספרס!\n\n"
        f"🛒 <b>לקנייה ישירה לחצו על הקישור:</b>\n"
        f"{clean_link}"
    )
    payload = {"chat_id": CHANNEL, "text": message_text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending: {e}")

def check_messages():
    last_id = 0
    url = f"https://telegram.org{TOKEN}/getUpdates"
    print("🚀 הבוט התניע מחדש ומקשיב להודעות...")
    
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
                                item_id = extract_item_id(text)
                                if item_id:
                                    aff_link = f"https://aliexpress.com{item_id}.html?trackingId={TRACKING_ID}"
                                    send_to_channel(aff_link)
                                    requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={
                                        "chat_id": cid, "text": "✅ הקישור פורסם בהצלחה בערוץ!"
                                    })
            elif res.status_code == 409:
                time.sleep(10)
        except Exception as e:
            pass
        time.sleep(1)

if __name__ == "__main__":
    check_messages()
