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
APP_URL = os.getenv("APP_URL")  # z. B. https://deutschmitmary-bot.up.railway.app
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"

# 🟢 Helper: prüft, ob dieser Post schon gesendet wurde (optional: erweitern mit DB oder Log)
sent_today = set()

async def start(update, context):
    await update.message.reply_text("✅ Der DeutschBot läuft stabil per Webhook!")

async def post_aus_json(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M")

    try:
        with open("posts.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
    except Exception as e:
        print(f"❌ Fehler beim Laden der posts.json: {e}")
        return

    for post in posts:
        zeit = post.get("zeit")
        text = post.get("text")
        bild = post.get("bild", "")
        audio = post.get("audio", "")
        uid = f"{zeit}|{text[:20]}"  # einfache ID zur Duplikatsvermeidung

        if zeit == now and uid not in sent_today:
            try:
                if bild:
                    await context.bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=bild,
                        caption=text,
                        parse_mode="MarkdownV2"
                    )
                elif audio:
                    await context.bot.send_voice(
                        chat_id=CHAT_ID,
                        voice=audio,
                        caption=text,
                        parse_mode="MarkdownV2"
                    )
                else:
                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=text,
                        parse_mode="MarkdownV2"
                    )
                sent_today.add(uid)
                print(f"✅ {zeit} – Beitrag gepostet: {post.get('typ')}")
            except Exception as e:
                print(f"❌ Fehler beim Posten um {zeit}: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # ⏰ Tägliche Posts prüfen: jede Minute
    app.job_queue.run_repeating(post_aus_json, interval=60, first=0)

    # 🚀 Webhook starten
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        allowed_updates=["message"]
    )

if __name__ == "__main__":
    main()
