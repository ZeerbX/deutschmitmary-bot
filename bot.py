from telegram.ext import ApplicationBuilder, ContextTypes
import datetime
import os

# Token und Chat-ID aus Railway Environment
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def post_daily_content(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%H:%M")
    print(f"📬 Poste um {now} Uhr")
    
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="📚 Wort des Tages: „lernen“ – یاد گرفتن"
    )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Zeiten in UTC → 08:00, 15:00, 19:00 MESZ
    application.job_queue.run_daily(post_daily_content, time=datetime.time(hour=6, minute=0))   # 08:00 MESZ
    application.job_queue.run_daily(post_daily_content, time=datetime.time(hour=13, minute=0))  # 15:00 MESZ
    application.job_queue.run_daily(post_daily_content, time=datetime.time(hour=17, minute=0))  # 19:00 MESZ

    print("✅ Bot läuft mit job_queue (Polling)")
    application.run_polling()

if __name__ == "__main__":
    main()
