import os
import requests
import telebot
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי יציב עבור Render שלא יקרוס
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. הגדרות ומשתני סביבה מהשרת
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def extract_product_id(text):
    """חילוץ מזהה מוצר מכל סוג של קישור עלי אקספרס"""
    # חיפוש קישור ארוך סטנדרטי
    product_id_match = re.search(r'item/(\d+)\.html', text)
    if not product_id_match:
        # חיפוש מספר רץ של ה-HTML
        product_id_match = re.search(r'(\d+)\.html', text)
    
    if product_id_match:
        return product_id_match.group(1)
    return None

@bot.message_handler(func=lambda message: True)
def handle_user_product(message):
    """פונקציה שקולטת קישור ששלחת לבוט, ממירה אותו ושולחת מייד לערוץ"""
    user_text = message.text
    print(f"📥 התקבל קישור ממך בבוט: {user_text}")
    
    # בדיקה אם ההודעה מכילה קישור של עלי אקספרס
    if "aliexpress" in user_text.lower() or "s.click" in user_text.lower():
        
        # חילוץ מזהה המוצר
        pid = extract_product_id(user_text)
        
        if pid:
            # בניית קישור שותפים תקין, רשמי ומדויק ב-100% ללא שברים
            affiliate_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
            
            # בניית פוסט נקי ומקצועי לערוץ שלך
            message_text = (
                f"🛍️ דיל חדש עלה לערוץ! 🛍️\n\n"
                f"🔥 מוצר מומלץ מעלי אקספרס במחיר מטורף!\n\n"
                f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
                f"{affiliate_link}"
            )
            
            try:
                # שליחת הפוסט לערוץ שלך (טלגרם תהפוך את הקישור לכחול ותטען את התמונה לבד!)
                bot.send_message(CHAT_ID, message_text, disable_web_page_preview=False)
                
                # שליחת הודעת אישור חזרה אליך לפרטי של הבוט
                bot.reply_to(message, "✅ הקישור הומר בהצלחה והפוסט שוגר לערוץ שלך!")
                print(f"🎯 פוסט עבור מוצר {pid} פורסם בהצלחה!")
            except Exception as e:
                bot.reply_to(message, f"❌ שגיאה בשליחה לערוץ: {e}")
        else:
            # אם שלחת קישור מקוצר (כמו s.click), נעביר אותו ישירות דרך מערכת ה-deepLink של השותפים
            clean_url = user_text.strip()
            affiliate_link = f"https://aliexpress.com{clean_url}&tracking_id={TRACKING_ID}"
            
            message_text = (
                f"🛍️ דיל חדש עלה לערוץ! 🛍️\n\n"
                f"🛒 לקנייה ישירה לחצו על הקישור הכחול:\n"
                f"{affiliate_link}"
            )
            try:
                bot.send_message(CHAT_ID, message_text, disable_web_page_preview=False)
                bot.reply_to(message, "✅ הקישור המקוצר הומר ושוגר בהצלחה!")
            except Exception as e:
                bot.reply_to(message, f"❌ שגיאה: {e}")
    else:
        bot.reply_to(message, "⚠️ נא לשלוח קישור תקין של עלי אקספרס בלבד.")

if __name__ == "__main__":
    print("🚀 בוט השליחה העצמית באוויר ומאזין לך בטלגרם...")
    # הפעלת האזנה קבועה ורציפה ללא הפסקה
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
