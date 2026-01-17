import os
import asyncio
from flask import Flask, request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ======================
# ENV / CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PAY_URL = os.getenv("PAY_URL", "https://global.tribopay.com.br/k08occpgzo")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").rstrip("/")  # ex: https://alexai2.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")        # opcional

if not BOT_TOKEN:
    raise RuntimeError("Missing BOT_TOKEN env var")

app = Flask(__name__)

# Telegram Application (python-telegram-bot 21.x)
tg_app = Application.builder().token(BOT_TOKEN).build()

# Event loop dedicado (estável com gunicorn worker sync)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ======================
# UI HELPERS
# ======================
def btn_pay(label: str = "💳 Pagar agora") -> InlineKeyboardButton:
    return InlineKeyboardButton(label, url=PAY_URL)

def kb_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Começar", callback_data="Q1")],
        [btn_pay("💳 Pagar agora")],
    ])

def kb_q2() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Continuar", callback_data="Q2")],
        [btn_pay("💳 Pagar agora")],
    ])

def kb_q3() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Continuar", callback_data="Q3")],
        [btn_pay("💳 Pagar agora")],
    ])

def kb_only_pay() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [btn_pay("🔒 Liberar acesso (Pagamento)")]
    ])

# ======================
# BOT HANDLERS
# ======================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Sem enrolação. Em poucos passos você escolhe e libera o acesso. 👇",
        reply_markup=kb_start()
    )

async def on_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "Q1":
        await query.edit_message_text(
            "Pergunta 1/3: Você prefere algo mais direto ou com mais narrativa?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Direto", callback_data="Q2")],
                [btn_pay("💳 Pagar agora")],
            ])
        )
        return

    if data == "Q2":
        await query.edit_message_text(
            "Pergunta 2/3: Você prefere receber em pacotes ou assinatura?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📦 Pacotes", callback_data="Q3")],
                [btn_pay("💳 Pagar agora")],
            ])
        )
        return

    if data == "Q3":
        await query.edit_message_text(
            "Pergunta 3/3: Último passo para liberar o acesso:",
            reply_markup=kb_only_pay()
        )
        return

# Registrar handlers
tg_app.add_handler(CommandHandler("start", start_cmd))
tg_app.add_handler(CallbackQueryHandler(on_click))

# ======================
# FLASK ROUTES
# ======================

# Healthcheck (endpoint único para evitar conflito)
@app.get("/", endpoint="health_root")
def health_root():
    return "OK", 200

# Webhook do Telegram (POST)
import traceback

@app.post("/webhook")
def telegram_webhook():
    try:
        # Proteção opcional (pode deixar)
        if WEBHOOK_SECRET:
            secret = request.headers.get("X-Webhook-Secret", "")
            if secret != WEBHOOK_SECRET:
                return "Unauthorized", 401

        payload = request.get_json(force=True, silent=True)
        if not isinstance(payload, dict):
            print("WEBHOOK ERROR: Payload inválido:", payload)
            return "Bad Request", 400

        update = Update.de_json(payload, tg_app.bot)
        loop.run_until_complete(tg_app.process_update(update))
        return "OK", 200

    except Exception as e:
        print("WEBHOOK ERROR:", repr(e))
        print(traceback.format_exc())
        return "Internal Server Error", 500

# Endpoint para setar webhook (aceita GET e POST pra evitar 405 no Render)
@app.route("/set-webhook", methods=["GET", "POST"], endpoint="set_webhook_route")
def set_webhook_route():
    if not WEBHOOK_URL:
        return "Missing WEBHOOK_URL env var", 500

    webhook_full = f"{WEBHOOK_URL}/webhook"
    ok = loop.run_until_complete(tg_app.bot.set_webhook(url=webhook_full))
    return f"Webhook set: {ok} => {webhook_full}", 200

# ======================
# LOCAL DEV (opcional)
# ======================
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

