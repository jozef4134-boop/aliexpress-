import os
import requests
import telebot
import time
from datetime import datetime
import pytz

# 1. הגדרת מפתחות ומשתני סביבה מהשרת
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
ALI_API_KEY = os.environ.get('ALI_API_KEY')
TRACKING_ID = os.environ.get('TRACKING_ID')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
israel_tz = pytz.timezone('Asia/Jerusalem')

# מילות מפתח ממוקדות לקטגוריות שביקשת
KEYWORDS = ["fitness", "gadgets", "tshirt", "earphones", "charger", "shoes", "clothing"]

# זיכרון יומי לשמירת הקישורים עבור הודעת הסיכום
daily_deals_summary = []

def get_hot_products():
    """משיכת מוצרים חמים וטרנדיים מאליאקספרס"""
    url = "https://aliexpress.com"
    search_query = " ".join(KEYWORDS)
    params = {
        'app_key': ALI_API_KEY,
        'tracking_id': TRACKING_ID,
        'keywords': search_query,
        'sort': 'VOLUME_DESC',
        'page_size': 40  # הגדלנו את הכמות כדי שנוכל לבחור 3 מוצרים טובים
    }
    try:
        response = requests.get(url, params=params).json()
        return response.get('result', {}).get('products', [])
    except Exception as e:
        print(f"שגיאה במשיכת מוצרים: {e}")
        return []

def check_and_post_3_products():
    """שליחת 3 מוצרים שעומדים בתנאי הסינון בבת אחת"""
    global daily_deals_summary
    products = get_hot_products()
    posted_count = 0
    
    for product in products:
        if posted_count >= 3:
            break  # עצרנו אחרי שפרסמנו בהצלחה 3 מוצרים
            
        try:
            original_price = float(product.get('original_price', 0))
            sale_price = float(product.get('sale_price', 0))
            title = product.get('product_title', '')
            image_url = product.get('product_main_image_url', '')
            affiliate_link = product.get('promotion_link', '')
        except (ValueError, TypeError):
            continue

        if original_price <= 0:
            continue

        discount_percent = ((original_price - sale_price) / original_price) * 100
        price_in_ils = sale_price * 3.65
        should_post = False
        
        # סינון לפי התנאים שלך
        if price_in_ils < 120 and discount_percent >= 30:
            should_post = True
        elif price_in_ils > 200 and discount_percent >= 50:
            should_post = True

        if should_post:
            short_description = " ".join(title.split()[:8])
            message_text = (
                f"🔥 **דיל חם ואטרקטיבי!** 🔥\n\n"
                f"📦 **מוצר:** {short_description}...\n"
                f"💰 **מחיר:** {price_in_ils:.2f} ₪\n"
                f"降低 **הנחה:** {discount_percent:.0f}%\n\n"
                f"👇 **לרכישה מהירה לחצו כאן:**\n{affiliate_link}"
            )
            try:
                bot.send_photo(CHAT_ID, image_url, caption=message_text, parse_mode='Markdown')
                # שמירה לסיכום היומי
                daily_deals_summary.append({"title": short_description, "link": affiliate_link})
                posted_count += 1
                time.sleep(5)  # מרווח קצר של 5 שניות בין מוצר למוצר כדי לא להעמיס
            except Exception as e:
                print(f"שגיאה בשליחת פוסט לטלגרם: {e}")

def send_daily_summary():
    """שליחת סיכום יומי של כל הדילים שנאספו במהלך היום"""
    global daily_deals_summary
    if not daily_deals_summary:
        return
        
    summary_text = "✨ 📜 **סיכום הדילים החמים של היום!** 📜 ✨\n"
    summary_text += "פספסתם משהו? הנה ריכוז של כל המוצרים השווים שעלו היום לערוץ:\n\n"
    
    for idx, deal in enumerate(daily_deals_summary, 1):
        summary_text += f"{idx}. [{deal['title']}]({deal['link']})\n"
        
    summary_text += "\n❤️ לילה טוב לכולם ונתראה מחר עם דילים חדשים!"
    
    try:
        bot.send_message(CHAT_ID, summary_text, parse_mode='Markdown', disable_web_page_preview=True)
        print("הודעת סיכום יומי נשלחה בהצלחה!")
        daily_deals_summary = []  # איפוס הרשימה ליום המחרת
    except Exception as e:
        print(f"שגיאה בשליחת סיכום יומי: {e}")

def main_loop():
    print("הבוט המשודרג הופעל ורץ ברקע...")
    
    while True:
        # בדיקת הזמן הנוכחי לפי שעון ישראל
        now = datetime.now(israel_tz)
        day_of_week = now.weekday()  # 4 = שישי, 5 = שבת, 6 = ראשון וכו'
        hour = now.hour
        minute = now.minute

        # 1. בדיקת השבתה (מיום שישי ב-15:00 עד מוצ"ש ב-20:00)
        if (day_of_week == 4 and hour >= 15) or (day_of_week == 5 and hour < 20):
            print(f"זמן מנוחה (שבת). השעה כעת: {now.strftime('%H:%M')}. הבוט ממתין...")
            time.sleep(1800)  # בדיקה חוזרת כל חצי שעה
            continue

        # 2. שליחת סיכום יום (בכל יום רגיל בשעה 23:00 בלילה)
        if hour == 23 and minute < 10:
            send_daily_summary()
            time.sleep(600)  # שינה ל-10 דקות כדי לא לשלוח פעמיים באותה שעה
            continue

        # 3. הרצה שעתית קבועה (רק בין 08:00 בבוקר ל-22:59 בלילה כדי לא להציק למשתמשים בלילה)
        if 8 <= hour <= 22:
            print(f"מפעיל ריצה שעתית: מפרסם 3 מוצרים... ({now.strftime('%H:%M')})")
            check_and_post_3_products()
            
        # המתנה של שעה שלמה (3600 שניות) עד לסבב הבא
        time.sleep(3600)

if __name__ == "__main__":
    main_loop()
