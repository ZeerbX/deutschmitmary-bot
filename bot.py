from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Bot-Token aus der Environment-Variable lesen
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Start-Befehl
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot ist online und bereit!")

# /getid-Befehl
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Deine Chat-ID ist: {update.effective_chat.id}")

# Hauptfunktion
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", get_id))
    app.run_polling()

if __name__ == "__main__":
    main()
