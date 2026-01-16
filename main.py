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
def pay_button(label: str = "💳 Pagar agora") -> InlineKeyboardButton:
    return InlineKeyboardButton(label, url=PAY_URL)

def keyboard_two(next_callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Continuar", callback_data=next_callback_data)],
        [pay_button("💳 Pagar agora")]
    ])

def keyboard_only_pay() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[pay_button("🔒 Liberar acesso (Pagamento)")]])

# ====== BOT FLOW ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Sem enrolação. Em poucos passos você escolhe e libera o acesso. 👇"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Começar", callback_data="Q1")],
        [pay_button("💳 Pagar agora")]
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
            [InlineKeyboardButton("⚡ Direto", callback_data="Q2")],
            [pay_button("💳 Pagar agora")]
        ])
        await query.edit_message_text(text, reply_markup=kb)
        return

    # Q2
    if data == "Q2":
        text = "Pergunta 2/3: Você prefere receber em pacotes ou assinatura?"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Pacotes", callback_data="Q3")],
            [pay_button("💳 Pagar agora")]
        ])
        await query.edit_message_text(text, reply_markup=kb)
        return

    # Q3
    if data == "Q3":
        text = "Pergunta 3/3: Perfeito. Último passo para liberar o acesso:"
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

@app.post("/webhook")
async def webhook():
    # Proteção básica opcional por header
    secret = request.headers.get("X-Webhook-Secret", "")
    if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
        return "Unauthorized", 401

    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    await tg_app.process_update(update)
    return "OK", 200

# ====== INIT WEBHOOK (chamado no start do Render) ======
@app.get("/set-webhook")
async def set_webhook():
    base_url = os.getenv("WEBHOOK_URL", "").rstrip("/")
    if not base_url:
        return "Missing WEBHOOK_URL env var", 500

    url = f"{base_url}/webhook"
    ok = await tg_app.bot.set_webhook(url=url)
    return f"Webhook set: {ok} => {url}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
