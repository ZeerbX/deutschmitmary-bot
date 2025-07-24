import os
import json
import random
from dotenv import load_dotenv
from telegram import Bot
from telegram.utils.helpers import escape_markdown

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
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_posted_id(post_id):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(post_id + "\n")

def find_unposted_post(posts, posted_ids):
    unposted = [p for p in posts if p["id"] not in posted_ids]
    return random.choice(unposted) if unposted else None

def post_to_telegram(post):
    raw_text = post["text"]
    text = escape_markdown(raw_text, version=2)
    image = post.get("bild")
    audio = post.get("audio")

    try:
        if image:
            bot.send_photo(chat_id=CHAT_ID, photo=image)
        if audio:
            bot.send_audio(chat_id=CHAT_ID, audio=audio)
        bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="MarkdownV2")
        print(f"✅ Beitrag {post['id']} erfolgreich gesendet")
    except Exception as e:
        print(f"❌ Fehler beim Senden von {post['id']}: {e}")

def main():
    posts = load_posts()
    posted_ids = load_posted_ids()
    post = find_unposted_post(posts, posted_ids)

    if not post:
        print("⚠️ Keine neuen Beiträge verfügbar.")
        return

    post_to_telegram(post)
    save_posted_id(post["id"])

if __name__ == "__main__":
    main()
