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

def fix_and_convert_link(text):
    """איתור קישורי עלי אקספרס והמרתם לקישור שותפים תקין ומובנה"""
    if not text:
        return ""
    urls = re.findall(r'(https?://[^\s]+aliexpress[^\s]+|https?://s\.click\.[^\s]+)', text)
    new_text = text
    
    for original_url in urls:
        clean_url = original_url.rstrip('.,;)!]')
        product_id_match = re.search(r'item/(\d+)\.html', clean_url)
        if not product_id_match:
            product_id_match = re.search(r'(\d+)\.html', clean_url)
            
        if product_id_match:
            pid = product_id_match.group(1)
            my_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
        else:
            my_link = f"https://aliexpress.com{clean_url}&tracking_id={TRACKING_ID}"
            
        new_text = new_text.replace(original_url, my_link)
        
    # הסרת קישורי הצטרפות לערוצים אחרים כדי שהערוץ שלך יהיה נקי
    new_text = re.sub(r'https?://t\.me/[^\s]+', '', new_text)
    return new_text

@bot.message_handler(content_types=['text', 'photo'])
def handle_forwarded_deal(message):
    """פונקציה שקולטת הודעה ששלחת או העברת לבוט, מעבדת אותה ומפרסמת בערוץ שלך"""
    try:
        print("📥 התקבלה הודעה חדשה בבוט! מתחיל עיבוד...")
        
        # חילוץ הטקסט בין אם זה פוסט רגיל או פוסט עם תמונה
        incoming_text = message.caption if message.content_type == 'photo' else message.text
        
        if not incoming_text:
            return
            
        # המרת הקישורים לקישורי השותפים שלך וניקוי פרסומות
        final_message = fix_and_convert_link(incoming_text)
        
        # הוספת חתימה קטנה ומקצועית של הערוץ שלך בסוף
        final_message += "\n\n💎 פורסם בערוץ דילים שווים 2026 💎"

        if message.content_type == 'photo':
            # אם יש תמונה, ניקח את הגרסה הגדולה ביותר שלה ונשלח לערוץ
            photo_id = message.photo[-1].file_id
            bot.send_photo(CHAT_ID, photo_id, caption=final_message)
            print("✅ הדיל נשלח בהצלחה לערוץ כולל התמונה המקורית!")
        else:
            # שליחת הודעת טקסט נקייה
            bot.send_message(CHAT_ID, final_message)
            print("✅ הדיל נשלח בהצלחה לערוץ כהודעת טקסט!")
            
    except Exception as e:
        print(f"❌ שגיאה בעיבוד ההודעה: {e}")

if __name__ == "__main__":
    print("🚀 בוט המאזין החכם באוויר ומוכן לקבל ממך הודעות...")
    # הפעלת האזנה קבועה ורציפה ללא הפסקה
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
