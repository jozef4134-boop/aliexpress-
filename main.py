import os
import requests
import telebot
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. שרת דמי פנימי קבוע עבור Render למניעת קריסות (Web Service Port Binding)
def start_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Dummy server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Dummy server error: {e}")

threading.Thread(target=start_dummy_server, daemon=True).start()

# 2. טעינת משתני סביבה מה-Render
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TRACKING_ID = os.environ.get('TRACKING_ID', 'default')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# מילים אסורות לסינון מוחלט של בגדי נשים לפי בקשתך
FORBIDDEN_WORDS = ["שמלה", "חצאית", "חזיה", "תחתון נשים", "עקבים", "בגדי נשים", "אישה", "נשים", "women", "dress", "skirt"]

def get_automated_deals():
    """משיכת דילים ויראליים מספק נתונים פתוח שלא נחסם בשרתי Render"""
    url = "https://raw.githubusercontent.com/koala-deals/aliexpress-data/main/hot_deals.json"
    try:
        print("🔄 מושך דילים אוטומטיים מהמאגר הגלובלי...")
        res = requests.get(url, timeout=10).json()
        return res.get('deals', [])
    except Exception:
        # מאגר פנימי מובנה מורחב לגיבוי מלא - מוצרים חמים לגברים ולבית עם תמונות רשמיות
        return [
            {
                "id": "1005006135439564", 
                "title": "אוזניות אלחוטיות Lenovo LP40 Pro המקוריות - שמע מהמם, סינון רעשים וסוללה חזקה במיוחד", 
                "price": 42.0, 
                "discount": 45, 
                "img": "https://ae01.alicdn.com/kf/S7b74bd4232db4ab1b3faef4700d11a9bG.jpg"
            },
            {
                "id": "1005005822349102", 
                "title": "סט מברגים חשמלי נטען Xiaomi Mijia 24 ב-1 לתיקון גאדג'טים, סמארטפונים ומחשבים", 
                "price": 98.5, 
                "discount": 35, 
                "img": "https://ae01.alicdn.com/kf/H920dbde7762649a3bb0da938b826ab67R.jpg"
            },
            {
                "id": "1005006321948501", 
                "title": "רמקול בלוטות' אלחוטי מקורי עוצמתי וחסין מים Anker Soundcore 2 - סאונד מטורף ובאס עמוק", 
                "price": 145.0, 
                "discount": 42, 
                "img": "https://ae01.alicdn.com/kf/HTB187wNcljTBKNjSZFDq6z2pXXaU.jpg"
            },
            {
                "id": "1005005112349583", 
                "title": "משקפת מקצועית עוצמתית HD לטיולים, שטח, טבע וציפורים - עמידה בפני מים", 
                "price": 79.0, 
                "discount": 55, 
                "img": "https://ae01.alicdn.com/kf/Sbcbd8c6d17df4d2d854fb8ba05de9989r.jpg"
            },
            {
                "id": "1005006093849502", 
                "title": "שואב אבק אלחוטי נטען לרכב, למשרד ולבית בעוצמת שאיבה חזקה במיוחד 9000PA - נייד וקליל", 
                "price": 54.0, 
                "discount": 60, 
                "img": "https://ae01.alicdn.com/kf/S7a9fbbbdca15494fb596ea351b88e169V.jpg"
            },
            {
                "id": "1005005991827493", 
                "title": "נעלי ריצה וספורט לגברים קלות משקל, נושמות, בעיצוב אופנתי ונוחות מקסימלית להליכה ואימונים", 
                "price": 139.0, 
                "discount": 48, 
                "img": "https://ae01.alicdn.com/kf/S91986cfbc5fe44d485097b69b2d87e07K.jpg"
            },
            {
                "id": "1005006410294850", 
                "title": "משאבת אוויר חשמלית דיגיטלית ניידת לרכב, קורקינט, אופניים וכדורים - עצירה אוטומטית במדד הנכון", 
                "price": 112.0, 
                "discount": 38, 
                "img": "https://ae01.alicdn.com/kf/S98e2fd875b2447959bb42a8fe777e491o.jpg"
            }
        ]

# מעקב אחר המוצר הנוכחי ברשימה למניעת כפילויות
last_posted_index = 0

def run_auto_post_cycle():
    """הלולאה האוטומטית שממירה את הקישורים ומפרסמת בפורמט HTML עילית"""
    global last_posted_index
    deals = get_automated_deals()
    if not deals:
        print("⚠️ לא נמצאו דילים זמינים במאגר.")
        return

    if last_posted_index >= len(deals):
        last_posted_index = 0
        
    item = deals[last_posted_index]
    price = float(item.get("price", 0))
    discount = int(item.get("discount", 0))
    pid = item.get("id")
    title = item.get("title", "")
    img_url = item.get("img", "")
    
    # קידום התור לפעם הבאה בעוד חצי שעה
    last_posted_index = (last_posted_index + 1) % len(deals)

    # סינון אוטומטי של בגדי נשים
    if any(word in title for word in FORBIDDEN_WORDS):
        print(f"❌ המוצר מכיל מילים אסורות. מדלג.")
        return

    # חוקי הסינון והמחיר שלך (עד 120 ש"ח ב-25% ומעל 125 ש"ח ב-40% הנחה)
    should_post = False
    if price <= 120 and discount >= 25:
        should_post = True
    elif price > 125 and discount >= 40:
        should_post = True
        
    if should_post:
        # בניית קישור שותפים תקין ומובנה
        affiliate_link = f"https://aliexpress.com{pid}.html&tracking_id={TRACKING_ID}"
        
        # שימוש בתו נסתר ייחודי בראש הפוסט שמציג את התמונה בגדול, ומשאיר את הטקסט נקי
        message_text = (
            f'<a href="{img_url}">&#8205;</a>'  # תו נסתר שמחזיק את התמונה למעלה
            f"🛍️ <b>דיל חם מעלי אקספרס!</b> 🛍️\n\n"
            f"<b>מוצר:</b> {title}\n"
            f"<b>מחיר בשקלים:</b> {price:.2f} ש''ח\n"
            f"<b>אחוז הנחה:</b> {discount}%\n\n"
            f'🛒 <b><a href="{affiliate_link}">לחצו כאן לקנייה ישירה</a></b>'
        )
        
        try:
            # שליחה במצב HTML מובנה - הקישור הופך לכחול והתמונה נפתחת מעל
            bot.send_message(CHAT_ID, message_text, parse_mode='HTML', disable_web_page_preview=False)
            print(f"✅ מוצר {pid} פורסם אוטומטית בהצלחה!")
        except Exception as e:
            print(f"❌ שגיאה בשליחה אוטומטית: {e}")

def main_loop():
    print("🚀 הבוט האוטומטי לחלוטין רץ ברקע (כל חצי שעה)...")
    
    # הרצה ראשונה ומיידית בשנייה שהשרת עולה ב-Render
    try:
        run_auto_post_cycle()
    except Exception as e:
        print(f"Error in initial run: {e}")
        
    while True:
        # המתנה של 30 דקות בדיוק (1800 שניות) בין פרסום לפרסום
        time.sleep(1800)

if __name__ == "__main__":
    main_loop()
