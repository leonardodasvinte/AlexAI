import os
import logging
import asyncio
from flask import Flask, request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM TOKEN")  # setar no Render
TRIBO_PAY_LINK = "https://global.tribopay.com.br/k08occpgzo"

GIF_INICIAL = "surpresa.gif"
FOTO_BOAS_VINDAS_1 = "boas_vindas_1.png"
FOTO_BOAS_VINDAS_2 = "boas_vindas_2.png"
FOTO_TEASER_1 = "foto_teaser_1.png"
FOTO_TEASER_2 = "foto_teaser_2.png"

app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    try:
        with open(GIF_INICIAL, "rb") as f:
            await context.bot.send_animation(chat_id=chat_id, animation=f)
    except Exception as e:
        logger.exception(f"Erro no GIF: {e}")

    try:
        with open(FOTO_BOAS_VINDAS_1, "rb") as f1, open(FOTO_BOAS_VINDAS_2, "rb") as f2:
            await context.bot.send_photo(chat_id=chat_id, photo=f1)
            await context.bot.send_photo(chat_id=chat_id, photo=f2)
    except Exception as e:
        logger.exception(f"Erro nas fotos boas-vindas: {e}")

    texto_boas = "Olá! Aqui tenho a surpresa especial pra você 🔥"
    keyboard = [[InlineKeyboardButton("Quero ver", callback_data="mais_brindes")]]
    await context.bot.send_message(
        chat_id=chat_id,
        text=texto_boas,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "mais_brindes":
        await context.bot.send_message(chat_id=chat_id, text="São coisas assim que você quer ver? 😏")
        try:
            with open(FOTO_TEASER_1, "rb") as f:
                await context.bot.send_photo(chat_id=chat_id, photo=f)
        except Exception as e:
            logger.exception(f"Erro foto teaser 1: {e}")

        keyboard = [[InlineKeyboardButton("Mais brindes", callback_data="mais_brindes_2")]]
        await context.bot.send_message(chat_id=chat_id, text="Quer mais?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "mais_brindes_2":
        await context.bot.send_message(chat_id=chat_id, text="Então toma...")
        try:
            with open(FOTO_TEASER_2, "rb") as f:
                await context.bot.send_photo(chat_id=chat_id, photo=f)
        except Exception as e:
            logger.exception(f"Erro foto teaser 2: {e}")

        keyboard_final = [[InlineKeyboardButton("Mais um, quero te ajudar", url=TRIBO_PAY_LINK)]]
        await context.bot.send_message(chat_id=chat_id, text="Último passo 👇", reply_markup=InlineKeyboardMarkup(keyboard_final))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start pra começar! 🔥")

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CallbackQueryHandler(button))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.get("/")
def home():
    return "Bot is running!"

@app.post("/webhook")
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    asyncio.run(tg_app.process_update(update))
    return "OK", 200

def setup_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    logger.info(f"Setting webhook to: {webhook_url}")
    asyncio.run(tg_app.bot.set_webhook(url=webhook_url))

if __name__ == "__main__":
    setup_webhook()
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

