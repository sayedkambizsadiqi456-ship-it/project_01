import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

RESTAURANT_NAME = "🍽️ Takhar Restaurant"
CONTACT_IMAGE_URL = "https://raw.githubusercontent.com/sayedkambizsadiqi456-ship-it/project_01/main/takhar_iletisim.png"

MENU = {
    "🥗 Meze & Salatalar": {
        "Cezar Salata": 25000,
        "Gavda Salata": 20000,
        "Haydari": 18000,
        "acz": 22000,
        "SIGARA BÖREK": 25000,
        "K培養": 30000
    },
    "🍖 Ana Yemekler": {
        "Takht Kebab": 180000,
        "Jooje Kebab": 150000,
        "Kashk Bademjan": 120000,
        "Gheyme": 140000,
        "Sibzam": 130000,
        "Kuku": 110000
    },
    "🍝 Makarnalar": {
        "Kal Peste": 90000,
        "Fosf": 85000,
        "riz": 80000
    },
    "🍰 Tatlılar": {
        "Baklava": 30000,
        "GZ": 25000,
        "Soos": 28000,
        "Sholeh Zard": 20000,
        "ice": 35000
    },
    "🥤 İçecekler": {
        "Ayran": 8000,
        "ş": 10000,
        "Kola": 15000,
        " soda": 12000,
        "Çay": 5000,
        "Kahve": 20000
    }
}

user_orders = {}
cart = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🍽️ Menüyü Görüntüle")],
        [KeyboardButton("🛒 Sepetim")],
        [KeyboardButton("📞 İletişim")],
        [KeyboardButton("📍 Konum")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"{RESTAURANT_NAME}\n\n"
        "🌟 Takhar Restoran'a Hoş Geldiniz!\n\n"
        "Sipariş vermek için menümüzü görüntüleyebilir\n"
        "veya aşağıdaki seçenekleri kullanabilirsiniz.",
        reply_markup=reply_markup
    )

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for category, items in MENU.items():
        item_text = "\n".join([f"  {name} - {price:,} T" for name, price in items.items()])
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])
    
    await update.message.reply_text(
        "🍽️ Menüyü Görüntüle\n\nBirini seçin:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo=CONTACT_IMAGE_URL)
    await update.message.reply_text(
        "📞 Takhar Restaurant İletişim\n\n"
        "📱 Telefon: +90 212 XXX XX XX\n"
        "✉️ Email: info@takhar-restaurant.com\n"
        "🕐 Çalışma Saatleri:\n"
        "  Pazartesi - Pazar: 09:00 - 23:00"
    )

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo=CONTACT_IMAGE_URL)
    await update.message.reply_text(
        "📍 Konum\n\n"
        "Adres: Takhar Restaurant\n İstanbul, Türkiye\n\n"
        "Harita konumu buraya gelecek"
    )

async def my_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in cart or not cart[chat_id]:
        await update.message.reply_text("🛒 Sepetiniz boş!")
        return
    
    total = sum(item["price"] * item["qty"] for item in cart[chat_id].values())
    text = "🛒 Sepetiniz:\n\n"
    for name, item in cart[chat_id].items():
        text += f"  {item['name']} x{item['qty']} = {item['price']*item['qty']:,} T\n"
    text += f"\n💰 Toplam: {total:,} T"
    
    keyboard = [
        [InlineKeyboardButton("✅ Siparişi Onayla", callback_data="confirm")],
        [InlineKeyboardButton("❌ Sepeti Temizle", callback_data="clear")],
        [InlineKeyboardButton("➕ Ürün Ekle", callback_data="add_more")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    
    if query.data == "confirm":
        if chat_id in cart and cart[chat_id]:
            total = sum(item["price"] * item["qty"] for item in cart[chat_id].values())
            await query.message.reply_text(
                f"✅ Siparişiniz alındı!\n\n"
                f"💰 Toplam: {total:,} T\n\n"
                f"Teşekkür ederiz! Takkar Restaurant"
            )
            cart[chat_id] = {}
        else:
            await query.message.reply_text("Sepetiniz boş!")
    
    elif query.data == "clear":
        cart[chat_id] = {}
        await query.message.reply_text("🗑️ Sepetiniz temizlendi!")
    
    elif query.data == "add_more":
        await show_menu_category(update, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🍽️ Menüyü Görüntüle":
        await show_menu_category(update, context)
    elif text == "🛒 Sepetim":
        await my_cart(update, context)
    elif text == "📞 İletişim":
        await contact(update, context)
    elif text == "📍 Konum":
        await location(update, context)
    elif text.startswith("➕") or text in [item for items in MENU.values() for item in items]:
        pass

async def show_menu_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for category in MENU.keys():
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])
    
    await update.message.reply_text(
        "🍽️ Menü Kategorileri\n\nBirini seçin:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")
    
    if category in MENU:
        text = f"{category}\n\n"
        for name, price in MENU[category].items():
            text += f"  {name} - {price:,} T\n"
        
        keyboard = [[InlineKeyboardButton("⬅️ Geri", callback_data="back")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("add_"):
        item_name = data.replace("add_", "")
        chat_id = query.message.chat.id
        
        for category, items in MENU.items():
            if item_name in items:
                if chat_id not in cart:
                    cart[chat_id] = {}
                if item_name in cart[chat_id]:
                    cart[chat_id][item_name]["qty"] += 1
                else:
                    cart[chat_id][item_name] = {
                        "name": item_name,
                        "price": items[item_name],
                        "qty": 1
                    }
                await query.message.reply_text(f"✅ {item_name} sepete eklendi!")
                break

async def main():
    app = Application.builder().token("8572653304:AAH0ffnfCfL1JcxGFMFvI6VV1usWL2z2itc").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(CommandHandler("cart", my_cart))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("location", location))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CallbackQueryHandler(category_selected, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Bot başlatıldı!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())