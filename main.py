import logging
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '8222338658:AAEfZx1O19Q-uvCed4jy4gH2-lMspiVylng'
TRIBO_PAY_LINK = 'https://global.tribopay.com.br/k08occpgzo'

GIF_INICIAL = 'surpresa.gif'
FOTO_BOAS_VINDAS_1 = 'boas_vindas_1.png'
FOTO_BOAS_VINDAS_2 = 'boas_vindas_2.png'
FOTO_TEASER_1 = 'foto_teaser_1.png'
FOTO_TEASER_2 = 'foto_teaser_2.png'

app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await context.bot.send_animation(chat_id=chat_id, animation=open(GIF_INICIAL, 'rb'))
    await context.bot.send_photo(chat_id=chat_id, photo=open(FOTO_BOAS_VINDAS_1, 'rb'))
    await context.bot.send_photo(chat_id=chat_id, photo=open(FOTO_BOAS_VINDAS_2, 'rb'))

    texto_boas = "Oláááá! Aqui tenho a surpresa especial pra você 🔥"
    keyboard = [
        [InlineKeyboardButton("Quer ver mais brindes?", callback_data='mais_brindes')],
        [InlineKeyboardButton("Já quero comprar", url=TRIBO_PAY_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=texto_boas, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == 'mais_brindes':
        texto1 = "São coisas assim que você quer ver? 😏"
        await context.bot.send_message(chat_id=chat_id, text=texto1)
        await context.bot.send_photo(chat_id=chat_id, photo=open(FOTO_TEASER_1, 'rb'))

        keyboard = [
            [InlineKeyboardButton("Mais brindes", callback_data='mais_brindes_2')],
            [InlineKeyboardButton("Tribo Pay", url=TRIBO_PAY_LINK)]
        ]
        await context.bot.send_message(
            chat_id=chat_id,
            text="Escolha:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'mais_brindes_2':
        texto2 = "Então toma..."
        await context.bot.send_message(chat_id=chat_id, text=texto2)
        await context.bot.send_photo(chat_id=chat_id, photo=open(FOTO_TEASER_2, 'rb'))

        keyboard_final = [
            [InlineKeyboardButton("Mais um, quero te ajudar", url=TRIBO_PAY_LINK)]
        ]
        await context.bot.send_message(
            chat_id=chat_id,
            text="Agora é com você 🔥",
            reply_markup=InlineKeyboardMarkup(keyboard_final)
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start pra começar! 🔥")

# Inicialização do bot
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return 'OK', 200

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    logger.info(f"Setting webhook to: {webhook_url}")
    import asyncio
    asyncio.run(application.bot.set_webhook(url=webhook_url))

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
