import os
import json
from datetime import datetime
from telegram import Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
PORT = int(os.environ.get("PORT", 8443))
APP_URL = os.getenv("APP_URL")  # z. B. https://deutschmitmary-bot-production.up.railway.app
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"


async def start(update, context):
    await update.message.reply_text("Bot läuft per Webhook 🚀")


async def getid(update, context):
    await update.message.reply_text(
        f"🆔 Deine Chat ID: `{update.effective_chat.id}`",
        parse_mode="MarkdownV2"
    )


async def post_aus_json(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M")
    print(f"⏰ Prüfung um {now}...")

    try:
        with open("posts.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der posts.json: {e}")
        return

    for post in posts:
        if post.get("zeit") == now:
            text = post.get("text", "Kein Text vorhanden.")
            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=text,
                    parse_mode="MarkdownV2"
                )
                print(f"✅ Beitrag gepostet um {now}: {text}")
            except Exception as e:
                print(f"❌ Fehler beim Senden: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", getid))

    # 🕒 Automatischer Post-Job: prüft jede Minute
    app.job_queue.run_repeating(post_aus_json, interval=60, first=0)

    # Webhook starten
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        allowed_updates=["message", "callback_query"]
    )


if __name__ == "__main__":
    main()
