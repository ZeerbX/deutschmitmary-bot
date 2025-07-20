import os
import json
import random
from datetime import datetime
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
APP_URL = os.getenv("APP_URL")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"


async def start(update, context):
    await update.message.reply_text("Bot läuft per Webhook 🚀")


async def getid(update, context):
    await update.message.reply_text(
        f"🆔 Deine Chat ID: `{update.effective_chat.id}`",
        parse_mode="MarkdownV2"
    )


def finde_zufalls_post(posts, typ, zeit):
    passende = [p for p in posts if p.get("typ") == typ and p.get("zeit") == zeit]
    return random.choice(passende) if passende else None


async def post_aus_json(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow().strftime("%H:%M")
    print(f"⏰ Prüfung um {now} UTC...")

    try:
        with open("posts.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der posts.json: {e}")
        return

    typ_zeit_map = {
        "06:00": "wort",
        "13:00": "grammatik",
        "17:00": "tipp"
    }

    if now in typ_zeit_map:
        typ = typ_zeit_map[now]
        post = finde_zufalls_post(posts, typ, now)

        if post:
            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=post.get("text", "Kein Text vorhanden."),
                    parse_mode="MarkdownV2"
                )
                print(f"✅ Beitrag gepostet ({typ}) um {now} UTC")
            except Exception as e:
                print(f"❌ Fehler beim Senden: {e}")
        else:
            print(f"⚠️ Kein {typ}-Post für {now} gefunden.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", getid))

    app.job_queue.run_repeating(post_aus_json, interval=60, first=0)

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        allowed_updates=["message", "callback_query"]
    )


if __name__ == "__main__":
    main()
