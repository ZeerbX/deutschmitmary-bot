from flask import Flask, request
import os
import json
import random
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTS_FILE = "posts.json"
POSTED_IDS_FILE = "posted_ids.txt"

bot = Bot(BOT_TOKEN)

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

def send_post():
    posts = load_posts()
    posted_ids = load_posted_ids()
    unposted = get_unposted_posts(posts, posted_ids)

    if not unposted:
        return "📛 Keine neuen Beiträge vorhanden."

    post = random.choice(unposted)
    post_id = post["id"]
    text = f"*{post['title']}*\n{post['text']}"
    media = post.get("media")

    try:
        if media:
            if media.endswith(".jpg") or media.endswith(".png"):
                bot.send_photo(chat_id=CHAT_ID, photo=media, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
            elif media.endswith(".mp3") or media.endswith(".ogg"):
                bot.send_audio(chat_id=CHAT_ID, audio=media, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
            else:
                bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        save_posted_id(post_id)
        return f"✅ Beitrag {post_id} wurde gesendet."
    except Exception as e:
        return f"⚠️ Fehler beim Senden: {str(e)}"

@app.route("/", methods=["GET"])
def health():
    return "✅ Bot ist bereit."

@app.route("/trigger", methods=["GET"])
def trigger():
    result = send_post()
    return result

if __name__ == "__main__":
    app.run(port=8080)
