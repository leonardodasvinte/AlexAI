import os
from flask import Flask, request
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ====== CONFIG ======
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PAY_URL = os.getenv("PAY_URL", "https://global.tribopay.com.br/k08occpgzo")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")  # simples proteção

if not BOT_TOKEN:
    raise RuntimeError("Missing BOT_TOKEN env var")

app = Flask(__name__)
tg_app = Application.builder().token(BOT_TOKEN).build()

# ====== HELPERS ======
def pay_button(label: str = "💳 Quero te ajuDAR") -> InlineKeyboardButton:
    return InlineKeyboardButton(label, url=PAY_URL)

def keyboard_two(next_callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Continuar", callback_data=next_callback_data)],
        [pay_button("💳 Quero te ajuDAR")]
    ])

def keyboard_only_pay() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[pay_button("🔒 Liberar acesso (Pagamento)")]])

# ====== BOT FLOW ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Oiiiii Delícia, vem ver comigo esse conteúdo bom que eu fiquei toda excitadinha fazendo?"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Quero ver delícia", callback_data="Q1")],
        [pay_button("Com certeza eu quero!")]
    ])
    await update.message.reply_text(text, reply_markup=kb)

async def on_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    # Q1
    if data == "Q1":
        text = "Pergunta 1/3: Você prefere algo mais direto ou com mais narrativa?"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Quer ver mais?!", callback_data="Q2")],
            [pay_button("💳 Quero te ajuDAR")]
        ])
        await query.edit_message_text(text, reply_markup=kb)
        return

    # Q2
    if data == "Q2":
        text = "Pergunta 2/3: Você prefere receber em pacotes ou assinatura?"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Brinde?!", callback_data="Q3")],
            [pay_button("💳 Quero te ajuDAR")]
        ])
        await query.edit_message_text(text, reply_markup=kb)
        return

    # Q3
    if data == "Q3":
        text = "Pergunta 3/3: Agora eu peço um favor pra nós dois...:"
        kb = keyboard_only_pay()
        await query.edit_message_text(text, reply_markup=kb)
        return

# ====== REGISTER HANDLERS ======
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CallbackQueryHandler(on_click))

# ====== FLASK WEBHOOK ======
@app.get("/")
def health():
    return "OK", 200

import os
import asyncio
from flask import Flask, request
from telegram import Update
# ... seus imports do telegram.ext e criação do tg_app e app ...

# Cria um event loop dedicado (estável no gunicorn sync)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ====== FLASK WEBHOOK ======
@app.get("/")
def health():
    return "OK", 200

@app.post("/webhook")
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    loop.run_until_complete(tg_app.process_update(update))
    return "OK", 200

# Aceita GET e POST pra não ficar 405 no Render
@app.route("/set-webhook", methods=["GET", "POST"])
def set_webhook():
    base_url = os.getenv("WEBHOOK_URL", "").rstrip("/")
    if not base_url:
        return "Missing WEBHOOK_URL env var", 500

    url = f"{base_url}/webhook"
    ok = loop.run_until_complete(tg_app.bot.set_webhook(url=url))
    return f"Webhook set: {ok} => {url}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))

