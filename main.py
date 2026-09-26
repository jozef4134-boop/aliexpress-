import os
import requests
import time
import threading
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי עבור Render למניעת קריסות של השירות
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. נתוני הבוט הרשמיים שלך (מחוברים קשיח לקוד)
TOKEN = "8810138861:AAFdsv00FYSF6hDrIffvAHA1PY144V61GcA"

# מאגר פסוקי תהילים מחזקים
TEHILIM_VERSES = [
    "📖 <b>ספר תהילים:</b>\n\n『 יְהוָה רֹעִי, לֹא אֶחְסָר. בִּנְאוֹת דֶּשֶׁא יַרְבִּיצֵנִי, עַל מֵי מְנֻחוֹת יְנַהֲלֵנִי. 』\n\n✨ השם ישמור אותך ואת משפחתך, בשורות טובות!",
    "📖 <b>ספר תהילים:</b>\n\n『 שִׁיר, לַמַּעֲלוֹת: אֶשָּׂא עֵינַי, אֶל-הֶהָרִים--מֵאַיִן, יָבֹא עֶזְרִי. עֶזְרִי, מֵעִם יְהוָה--עֹשֵׂה, שָׁמַיִם וָאָרֶץ. 』\n\n✨ ישועת השם כהרף עין! ברכה והצלחה בכל מעשה ידיך.",
    "📖 <b>ספר תהילים:</b>\n\n『 יְהוָה שֹׁמְרֶךָ, יְהוָה צִלְּךָ עַל יַד יְמִינֶךָ. יוֹמָם הַשֶּׁמֶשׁ לֹא יַכֶּכָּה וְיָרֵחַ בַּלָּיְלָה. 』\n\n✨ שמירה עליונה והגנה מכל רע מעכשיו ועד עולם.",
    "📖 <b>ספר תהילים:</b>\n\n『 קַוֵּה אֶל יְהוָה חֲזַק וְיַאֲמֵץ לִבֶּךָ וְקַוֵּה אֶל יְהוָה. 』\n\n✨ אל תירא ואל תפחד, הישועה קרובה לבוא. חזק וברוך!",
    "📖 <b>ספר תהילים:</b>\n\n『 גּוֹל עַל יְהוָה דַּרְכֶּךָ וּבְטַח עָלָיו וְהוּא יַעֲשֶׂה. 』\n\n✨ שים מבטחך בבורא עולם והכל יסתדר לטובה בקרוב מאוד."
]

def check_messages():
    # מחיקת היסטוריית ההודעות הישנה משרתי טלגרם בשנייה הזו
    url = f"https://telegram.org{TOKEN}/getUpdates"
    try:
        # שליחת בקשה עם offset=-1 מנקה לחלוטין את כל התור הישן של עלי אקספרס
        requests.get(url, params={"offset": -1, "timeout": 1})
        print("🧹 כל ההיסטוריה הישנה של טלגרם נמחקה בהצלחה!")
    except:
        pass

    last_id = 0
    print("🚀 בוט תהילים נקי התניע ומקשיב רק להודעות חדשות...")
    
    while True:
        try:
            payload = {"offset": last_id + 1, "timeout": 30}
            res = requests.get(url, params=payload, timeout=35)
            
            if res.status_code == 200:
                response = res.json()
                if "result" in response:
                    for update in response["result"]:
                        last_id = update["update_id"]
                        
                        if "message" in update and "chat" in update["message"]:
                            chat_id = update["message"]["chat"]["id"]
                            print(f"📩 התקבלה הודעה חדשה, שולח תהילים ל: {chat_id}")
                            
                            chosen_verse = random.choice(TEHILIM_VERSES)
                            
                            send_url = f"https://telegram.org{TOKEN}/sendMessage"
                            send_payload = {
                                "chat_id": chat_id,
                                "text": chosen_verse,
                                "parse_mode": "HTML"
                            }
                            requests.post(send_url, json=send_payload, timeout=10)
                            print("🎯 פסוק תהילים נשלח!")
                            
            elif res.status_code == 409:
                time.sleep(5)
        except Exception as e:
            time.sleep(5)
        time.sleep(1)

if __name__ == "__main__":
    check_messages()
