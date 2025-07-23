import os
import json
import random
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

# 🔐 Lade Umgebungsvariablen
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTS_FILE = "posts.json"
POSTED_FILE = "posted_ids.txt"

bot = Bot(token=BOT_TOKEN)

# 📦 Beiträge laden
def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 📁 IDs der geposteten Beiträge laden
def load_posted_ids():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(line.strip() for line in f)

# ✍️ Neue ID speichern
def save_posted_id(post_id):
    with open(POSTED_FILE, "a") as f:
        f.write(post_id + "\n")

# ✅ Escape-Funktion für MarkdownV2
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

# 🔍 Wähle nächsten ungesendeten Beitrag
def get_next_post():
    posts = load_posts()
    posted = load_posted_ids()
    candidates = [p for p in posts if p["id"] not in posted]
    return random.choice(candidates) if candidates else None

# 📤 Sende Beitrag
def send_post():
    post = get_next_post()
    if not post:
        print("❌ Keine neuen Beiträge.")
        return

    text = escape_markdown(post.get("text", ""))
    post_id = post["id"]
    image = post.get("bild")
    audio = post.get("audio")
    video = post.get("video")
    document = post.get("document")
    voice = post.get("voice")

    try:
        # 🎯 Medienlogik
        if image:
            bot.send_photo(chat_id=CHAT_ID, photo=image, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        elif video:
            bot.send_video(chat_id=CHAT_ID, video=video, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        elif document:
            bot.send_document(chat_id=CHAT_ID, document=document, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        elif audio:
            bot.send_audio(chat_id=CHAT_ID, audio=audio)
            bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        elif voice:
            bot.send_voice(chat_id=CHAT_ID, voice=voice)
            bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN_V2)

        save_posted_id(post_id)
        print(f"✅ Beitrag {post_id} erfolgreich gesendet.")
    except Exception as e:
        print(f"❌ Fehler beim Senden von {post_id}: {e}")

# 🟢 Starte sofort bei Railway-Aufruf
if __name__ == "__main__":
    send_post()
