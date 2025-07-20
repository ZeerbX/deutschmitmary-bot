import os
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
PORT = int(os.environ.get("PORT", 8443))
APP_URL = os.getenv("APP_URL")  # z. B. https://deutschmitmary-bot.up.railway.app
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"


async def start(update, context):
    await update.message.reply_text("Bot läuft per Webhook 🚀")


async def getid(update, context):
    await update.message.reply_text(f"🆔 Deine Chat ID: `{update.effective_chat.id}`", parse_mode="MarkdownV2")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", getid))

    # Webhook starten
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        allowed_updates=["message", "callback_query"]
    )


if __name__ == "__main__":
    main()
