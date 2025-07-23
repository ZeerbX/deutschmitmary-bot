import os
import json
import random
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

# .env laden
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTS_FILE = "posts.json"
POSTED_FILE = "posted_ids.txt"

bot = Bot(token=BOT_TOKEN)

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

def send_post():
    post = get_next_post()
    if not post:
        print("❌ Keine neuen Beiträge.")
        return

    text = post.get("text", "")
    image = post.get("bild")
    audio = post.get("audio")

    try:
        if image:
            bot.send_photo(chat_id=CHAT_ID, photo=image, caption=text)
        elif audio:
            bot.send_audio(chat_id=CHAT_ID, audio=audio, caption=text)
        else:
            bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)

        save_posted_id(post["id"])
        print(f"✅ Beitrag {post['id']} erfolgreich gesendet.")
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")

if __name__ == "__main__":
    send_post()
