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
MY_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# רשימת שמות המשתמש (Username) של ערוצי הדילים האחרים שאתה רוצה לסרוק מהם
# תוכל להחליף או להוסיף כאן כל ערוץ שתרצה (בלי ה-@)
CHANNELS_TO_SPY = ["dilimshavima", "israel_deals"]

# מילים חסומות לסנון בגדי נשים ומוצרים לא רצויים
BLOCKED_KEYWORDS = ["אישה", "נשים", "שמלה", "חצאית", "חזיה", "איפור", "עגילים"]

@bot.channel_post_handler(func=lambda message: True)
def handle_incoming_deals(message):
    """פונקציה שמקשיבה לערוצים האחרים, מעתיקה ומחליפה לקישור שלך"""
    try:
        # בדיקה אם הפוסט מגיע מאחד הערוצים שאנחנו עוקבים אחריהם
        if message.chat.username not in CHANNELS_TO_SPY:
            return

        text_content = message.text or message.caption or ""
        
        # 1. סינון בגדי נשים - אם קיימת מילה חסומה, נתעלם מהפוסט לחלוטין
        if any(keyword in text_content for keyword in BLOCKED_KEYWORDS):
            print("🚫 הפוסט סונן מכיוון שהוא מכיל מילים חסומות (מוצרי נשים).")
            return

        # 2. איתור מספר המוצר של אליאקספרס מתוך הקישור של הערוץ האחר
        # מחפש מספרים באורך 16 ספרות שמאפיינים מוצרים באליאקספרס
        product_ids = re.findall(r'100500\d{10}', text_content)
        
        if not product_ids:
            print("⚠️ לא נמצא מספר מוצר תקין של אליאקספרס בפוסט הנוכחי.")
            return
            
        pid = product_ids[0] # לוקח את המוצר הראשון שנמצא

        # 3. בניית הקישור החדש והנורמלי שלך עם ה-Tracking ID שלך!
        my_affiliate_link = f"https://aliexpress.com{pid}.html?sourceType=affiliate&trackingId={TRACKING_ID}"

        # 4. ניקוי הקישורים הישנים מהטקסט המקורי והחלפתם בקישור שלך
        # נשמור על התיאור המקורי, המחיר והאימוג'ים שהם כבר עיצבו בעברית!
        clean_text = re.sub(r'https?://\S+', '', text_content) # מוחק קישורים ישנים
        
        final_message = (
            f"{clean_text}\n\n"
            f"🛒 <b>לקנייה ישירה לחצו כאן:</b>\n"
            f"{my_affiliate_link}"
        )

        # 5. שליחת הפוסט המועתק והמשודרג ישירות לערוץ שלך
        if message.photo:
            # אם יש לפוסט תמונה, נשלח אותה יחד עם הטקסט החדש שלך
            photo_id = message.photo[-1].file_id
            bot.send_photo(MY_CHAT_ID, photo_id, caption=final_message, parse_mode='HTML')
            print(f"🎯 הצלחה מטורפת! הדיל הועתק, הקישור הוחלף לשלך והועלה עם תמונה!")
        else:
            # אם זה פוסט טקסט בלבד
            bot.send_message(MY_CHAT_ID, final_message, parse_mode='HTML')
            print(f"🎯 הצלחה! הדיל הועתק והועלה כטקסט בהצלחה!")

    except Exception as e:
        print(f"❌ שגיאה בעיבוד הפוסט מהערוץ המקביל: {e}")

if __name__ == "__main__":
    print("🚀 בוט הריגול והעתקת הדילים האוטומטי התחיל לעבוד ברקע...")
    
    try:
        bot.remove_webhook()
        bot.get_updates(offset=-1)
        time.sleep(1)
    except:
        pass
        
    # הפעלה קבועה של הצינתור וההקשבה לערוצים
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
