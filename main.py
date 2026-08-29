import os
import requests
import telebot

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
ALI_API_KEY = os.environ.get('ALI_API_KEY')
TRACKING_ID = os.environ.get('TRACKING_ID')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
KEYWORDS = ["fitness", "gadgets", "tshirt", "earphones", "charger", "shoes", "clothing"]

def get_hot_products():
    url = "https://aliexpress.com"
    search_query = " ".join(KEYWORDS)
    params = {
        'app_key': ALI_API_KEY,
        'tracking_id': TRACKING_ID,
        'keywords': search_query,
        'sort': 'VOLUME_DESC',
        'page_size': 20
    }
    try:
        response = requests.get(url, params=params).json()
        return response.get('result', {}).get('products', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def check_discounts_and_post():
    products = get_hot_products()
    for product in products:
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
        
        if price_in_ils < 120 and discount_percent >= 30:
            should_post = True
        elif price_in_ils > 200 and discount_percent >= 50:
            should_post = True

        if should_post:
            short_description = " ".join(title.split()[:10])
            message_text = (
                f"🔥 **דיל חם ואטרקטיבי במיוחד!** 🔥\n\n"
                f"📦 **מוצר:** {short_description}...\n"
                f"💰 **מחיר סופי:** {price_in_ils:.2f} ₪\n"
                f"📉 **הנחה מטורפת של:** {discount_percent:.0f}%\n\n"
                f"👇 **לרכישה מהירה לחצו כאן:**\n{affiliate_link}"
            )
            try:
                bot.send_photo(CHAT_ID, image_url, caption=message_text, parse_mode='Markdown')
                print(f"Posted: {short_description}")
                break
            except Exception as e:
                print(f"Telegram error: {e}")

if __name__ == "__main__":
    check_discounts_and_post()
