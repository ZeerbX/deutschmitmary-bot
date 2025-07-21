from telegram.ext import ApplicationBuilder, ContextTypes
from telegram.ext import JobQueue
import datetime
import os
from dotenv import load_dotenv

# .env laden (falls verwendet)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")  # oder direkt Token als String: "123456:ABCDEF..."

# Diese Funktion wird 3x täglich automatisch ausgeführt
async def post_daily_content(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%H:%M")
    print(f"📬 Poste um {now} Uhr")
    
    # Beispiel-Post
    await context.bot.send_message(
        chat_id="@almani_amuzesh",  # Gruppenname oder Chat-ID
        text="📚 Wort des Tages: „lernen“ – یاد گرفتن"
    )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Zeiten in UTC (entspricht 08:00, 15:00, 19:00 MESZ)
    application.job_queue.run_daily(post_daily_content, time=datetime.time(hour=6, minute=0))   # 08:00 MESZ
    application.job_queue.run_daily(post_daily_content, time=datetime.time(hour=13, minute=0))  # 15:00 MESZ
    application.job_queue.run_daily(post_daily_content, time=datetime.time(hour=17, minute=0))  # 19:00 MESZ

    print("🚀 Bot läuft mit job_queue (Polling)")
    application.run_polling()

if __name__ == "__main__":
    main()
