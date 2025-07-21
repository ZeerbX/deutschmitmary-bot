import os
import json
import random
from fastapi import FastAPI
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTS_FILE = "posts.json"
POSTED_FILE = "posted_ids.txt"

bot = Bot(token=BOT_TOKEN)
app = FastAPI()


def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_posted_ids():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_posted_id(post_id):
    with open(POSTED_FILE, "a") as f:
        f.write(post_id + "\n")


def get_next_post():
    posts = load_posts()
    posted = load_posted_ids()
    candidates = [p for p in posts if p["id"] not in posted]
    return random.choice(candidates) if candidates else None


@app.get("/trigger")
async def trigger_post():
    post = get_next_post()
    if not post:
        return {"status": "❌ Keine neuen Beiträge"}

    text = post.get("text", "")
    image = post.get("bild")
    audio = post.get("audio")

    try:
        if image:
            await bot.send_photo(chat_id=CHAT_ID, photo=image)
        if audio:
            await bot.send_audio(chat_id=CHAT_ID, audio=audio)

        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)
        save_posted_id(post["id"])
        return {"status": f"✅ Beitrag {post['id']} gesendet"}
    except Exception as e:
        return {"status": f"❌ Fehler beim Senden: {e}"}
