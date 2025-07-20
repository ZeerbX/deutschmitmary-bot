import json
import os
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, ContextTypes
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")  # <- Token als Railway-Secret

# Chat-ID deiner Gruppe (z. B. -1001234567890)
CHAT_ID = os.getenv("CHAT_ID")

# Pfad zur Datei mit den geplanten Beiträgen
POSTS_FILE = "post.json"


async def send_scheduled_post(application: Application):
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for post in posts:
            if post["datetime"] == now:
                await application.bot.send_message(chat_id=CHAT_ID, text=post["text"], parse_mode="HTML")
                break

    except Exception as e:
        print(f"[Fehler beim Senden des Beitrags] {e}")


async def run_scheduler(application: Application):
    while True:
        await send_scheduled_post(application)
        await asyncio.sleep(60)


async def main_async():
    application = Application.builder().token(BOT_TOKEN).build()

    # Starte Scheduler-Loop im Hintergrund
    asyncio.create_task(run_scheduler(application))

    # Starte Bot (auch wenn er keine Commands hat)
    await application.run_polling()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
