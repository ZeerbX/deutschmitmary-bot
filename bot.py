import os
import json
import random
from fastapi import FastAPI
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

# .env laden (für Railway-Umgebung mit Variablen funktioniert das auch so)
load_dotenv()

# Bot-Konfiguration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTS_FILE = "posts.json"
POSTED_FILE = "posted_ids.txt"

# Initialisiere Telegram-Bot und FastAPI
bot = Bot(token=BOT_TOKEN)
app = FastAPI()


def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_posted_ids():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_posted_id(post_id):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(post_id + "\n")


def get_next_post():
    posts = load_posts()
    posted = load_posted_ids()
    remaining = [p for p in posts if p["id"] not in posted]
    return random.choice(remaining) if remaining else None


@app.get("/trigger")
async def trigger_post():
    post = get_next_post()
    if not post:
        return {"status": "❌ Keine neuen Beiträge mehr vorhanden."}

    try:
        text = post.get("text", "")
        image = post.get("bild")
        audio = post.get("audio")

        if image:
            await bot.send_photo(chat_id=CHAT_ID, photo=image)
        if audio:
            await bot.send_audio(chat_id=CHAT_ID, audio=audio)

        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)
        save_posted_id(post["id"])

        return {"status": f"✅ Beitrag {post['id']} erfolgreich gesendet."}

    except Exception as e:
        return {"status": f"❌ Fehler beim Senden: {str(e)}"}
