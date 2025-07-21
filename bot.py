# bot.py
import os
import json
import logging
import random
from datetime import datetime
from telegram import Bot, InputFile
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes, JobQueue
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTS_FILE = "posts.json"
POSTED_IDS_FILE = "posted_ids.txt"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Hilfsfunktionen

def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_posted_ids():
    if not os.path.exists(POSTED_IDS_FILE):
        return set()
    with open(POSTED_IDS_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_posted_id(post_id):
    with open(POSTED_IDS_FILE, "a") as f:
        f.write(post_id + "\n")

def get_unposted_posts(posts, posted_ids):
    return [p for p in posts if p["id"] not in posted_ids]

# Hauptfunktion
async def send_random_post(context: ContextTypes.DEFAULT_TYPE):
    posts = load_posts()
    posted_ids = load_posted_ids()
    unposted = get_unposted_posts(posts, posted_ids)

    if not unposted:
        logging.info("📛 Keine neuen Beiträge vorhanden.")
        return

    post = random.choice(unposted)
    post_id = post["id"]
    text = f"*{post['title']}*\n{post['text']}"

    # Medien anhängen, wenn vorhanden
    if media := post.get("media"):
        if media.endswith(".jpg") or media.endswith(".png"):
            await context.bot.send_photo(chat_id=CHAT_ID, photo=media, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        elif media.endswith(".mp3") or media.endswith(".ogg"):
            await context.bot.send_audio(chat_id=CHAT_ID, audio=media, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)

    save_posted_id(post_id)
    logging.info(f"✅ Beitrag {post_id} wurde gesendet.")

# Bot-Start
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    job_queue: JobQueue = app.job_queue

    # Zeiten: 06:00, 13:00, 17:00 UTC (entspricht MESZ 08:00, 15:00, 19:00)
    job_queue.run_daily(send_random_post, time=datetime.strptime("06:00", "%H:%M").time(), name="Morning")
    job_queue.run_daily(send_random_post, time=datetime.strptime("13:00", "%H:%M").time(), name="Afternoon")
    job_queue.run_daily(send_random_post, time=datetime.strptime("17:00", "%H:%M").time(), name="Evening")

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
