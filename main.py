import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import asyncio

# URLs das imagens no GitHub RAW
IMG_Q1 = "https://raw.githubusercontent.com/leonardodasvinte/AlexAI/main/boas_vindas_1.png"
IMG_Q2 = "https://raw.githubusercontent.com/leonardodasvinte/AlexAI/main/boas_vindas_2.png"
IMG_Q3 = "https://raw.githubusercontent.com/leonardodasvinte/AlexAI/main/foto_teaser_1.png"

# URL de pagamento (exemplo, ajuste para sua URL)
PAY_URL = "https://global.tribopay.com.br/k08occpgzo"

# Inicializa o bot e Flask
BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)
tg_app = Application.builder().token(BOT_TOKEN).build()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Handlers do bot
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Sem enrolação. Em poucos passos você escolhe e libera o acesso. 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Começar", callback_data="Q1")],
            [InlineKeyboardButton("💳 Pagar agora", url=PAY_URL)],
        ])
    )

async def on_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    await query.answer()

    chat_id = query.message.chat.id

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    if data == "Q1":
        await context.bot.send_photo(chat_id=chat_id, photo=IMG_Q1)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Pergunta 1/3: Você prefere algo mais direto ou com mais narrativa?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Direto", callback_data="Q2")],
                [InlineKeyboardButton("💳 Pagar agora", url=PAY_URL)],
            ])
        )

    elif data == "Q2":
        await context.bot.send_photo(chat_id=chat_id, photo=IMG_Q2)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Pergunta 2/3: Você prefere receber em pacotes ou assinatura?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📦 Pacotes", callback_data="Q3")],
                [InlineKeyboardButton("💳 Pagar agora", url=PAY_URL)],
            ])
        )

    elif data == "Q3":
        await context.bot.send_photo(chat_id=chat_id, photo=IMG_Q3)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Pergunta 3/3: Último passo para liberar o acesso:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔒 Liberar acesso (Pagamento)", url=PAY_URL)]
            ])
        )

# Adiciona handlers ao bot
tg_app.add_handler(CommandHandler("start", start_cmd))
tg_app.add_handler(CallbackQueryHandler(on_click))

# Inicializa a aplicação do bot (necessário para process_update)
loop.run_until_complete(tg_app.initialize())
loop.run_until_complete(tg_app.start())

# Rota de health check
@app.get("/", endpoint="health_root")
def health_root():
    return "OK", 200

# Rota de webhook para Telegram
@app.post("/webhook")
def telegram_webhook():
    try:
        payload = request.get_json(force=True, silent=True)
        if not isinstance(payload, dict):
            return "Bad Request", 400

        update = Update.de_json(payload, tg_app.bot)
        loop.run_until_complete(tg_app.process_update(update))
        return "OK", 200

    except Exception as e:
        print("WEBHOOK ERROR:", repr(e))
        return "Internal Server Error", 500

# Rota para setar o webhook
@app.route("/set-webhook", methods=["GET", "POST"], endpoint="set_webhook_route")
def set_webhook_route():
    base_url = "https://SEU_DOMINIO.onrender.com"  # ajuste o domínio
    webhook_full = f"{base_url}/webhook"
    ok = loop.run_until_complete(tg_app.bot.set_webhook(url=webhook_full))
    return f"Webhook set: {ok} => {webhook_full}", 200

# Rodar localmente (opcional)
if __name__ == "__main__":
    port = int("10000")  # ou use os.getenv("PORT")
    app.run(host="0.0.0.0", port=port)





