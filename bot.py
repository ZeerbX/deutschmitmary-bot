import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Logging aktivieren (hilfreich für Railway-Logs)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start-Befehl
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Willkommen bei @DeutschmitMary_bot!")

# /getid-Befehl
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🆔 Deine Chat ID: `{chat_id}`", parse_mode="Markdown")

# Entry-Point
def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN nicht gefunden. Bitte als Environment-Variable setzen.")

    app = ApplicationBuilder().token(token).build()

    # Befehle registrieren
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", get_id))

    print("✅ Bot läuft...")
    app.run_polling()

if __name__ == "__main__":
    main()
