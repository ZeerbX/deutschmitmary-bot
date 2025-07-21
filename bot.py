import os
import json
import random
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastapi import FastAPI
import uvicorn

from telegram import Bot, InputFile
from telegram.constants import ParseMode
from telegram.ext import Application, ApplicationBuilder, ContextTypes

# ⬇️ ENV laden
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTS_FILE = "posts.json"
POSTED_IDS_FILE = "posted_ids.txt"

# ⬇️ Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ⬇️ Hilfsfunktionen
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

# ⬇️ Zufälliger Beitrag posten
async def send_random_post(bot: Bot):
    posts = load_posts()
    posted_ids = load_posted_ids()
    unposted = get_unposted_posts(posts, posted_ids)

    if not unposted:
        logging.info("📛 Keine neuen Beiträge vorhanden.")
        return

    post = random.choice(unposted)
    post_id = post["id"]
    text = f"*{post['title']}*\n{post['text']}"

    try:
        if media := post.get("media"):
            if media.endswith(".jpg") or media.endswith(".png"):
                await bot.send_photo(chat_id=CHAT_ID, photo=media, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
            elif media.endswith(".mp3") or media.endswith(".ogg"):
                await bot.send_audio(chat_id=CHAT_ID, audio=media, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
            else:
                await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)

        save_posted_id(post_id)
        logging.info(f"✅ Beitrag {post_id} wurde gesendet.")
    except Exception as e:
        logging.error(f"❌ Fehler beim Senden des Beitrags {post_id}: {e}")

# ⬇️ FastAPI & Trigger-Endpunkt
app = FastAPI()
app_bot: Bot = None

@app.get("/trigger")
async def trigger_post():
    now = datetime.utcnow() + timedelta(hours=2)  # MESZ
    current_hour = now.hour

    if current_hour in [9, 15, 19]:  # MESZ Zielzeiten
        logging.info(f"⏰ Trigger {current_hour}:00 erkannt – Beitrag wird gesendet.")
        await send_random_post(app_bot)
        return {"status": "posted", "time": f"{current_hour}:00"}
    else:
        logging.info(f"🕒 Trigger {current_hour}:00 ignoriert – keine gültige Zielzeit.")
        return {"status": "skipped", "time": f"{current_hour}:00"}

# ⬇️ App starten
async def start():
    global app_bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot = application.bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Damit Bot sofort aktiv ist (optional)

if __name__ == "__main__":
    import asyncio
    asyncio.get_event_loop().create_task(start())
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
