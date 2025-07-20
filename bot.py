
import json
import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import Updater, CallbackContext, JobQueue
import os

# === KONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token aus Railway-Umgebung
CHAT_ID = os.getenv("CHAT_ID")      # Telegram-Chat-ID (z. B. @almani_amuzesh)

# === POSTING-FUNKTION ===
def post_scheduled_message(context: CallbackContext):
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    with open("posts.json", "r", encoding="utf-8") as file:
        posts = json.load(file)

    for post in posts:
        if post["date"] == today and post["time"] == current_time:
            text = post["text"]
            context.bot.send_message(
                chat_id=CHAT_ID,
                text=text,
                parse_mode=ParseMode.MARKDOWN_V2
            )

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    job_queue: JobQueue = updater.job_queue

    # Jede Minute prüfen, ob etwas gepostet werden muss
    job_queue.run_repeating(post_scheduled_message, interval=60, first=5)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
