from telegram.ext.webhookhandler import WebhookServer
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.ext import ContextTypes
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
PORT = int(os.environ.get("PORT", 8443))
APP_URL = os.getenv("APP_URL")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"

POSTS_FILE = "posts.json"
POSTED_FILE = "posted_ids.json"

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Fehler beim Laden von posts.json: {e}")
        return []

def load_posted_ids():
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_posted_ids(ids):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

async def post_zur_uhrzeit(bot):
    now_utc = datetime.utcnow().strftime("%H:%M")
    print(f"⏰ Sofortige Prüfung beim Start um {now_utc} UTC")

    posts = load_posts()
    posted_ids = load_posted_ids()

    candidates = [p for p in posts if p.get("zeit") == now_utc and p.get("id") not in posted_ids]

    if not candidates:
        print("ℹ️ Kein neuer Beitrag für diese Zeit gefunden.")
        return

    post = random.choice(candidates)
    text = escape_markdown(post.get("text", ""))
    image = post.get("bild")
    audio = post.get("audio")

    try:
        if image:
            await bot.send_photo(chat_id=CHAT_ID, photo=image)
        if audio:
            await bot.send_audio(chat_id=CHAT_ID, audio=audio)
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="MarkdownV2")
        print(f"✅ Beitrag gepostet: {post.get('id')}")
        posted_ids.append(post.get("id"))
        save_posted_ids(posted_ids)
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")

async def start(update, context):
    await update.message.reply_text("✅ Bot läuft.")

async def getid(update, context):
    await update.message.reply_text(
        f"🆔 Deine Chat ID: `{update.effective_chat.id}`",
        parse_mode="MarkdownV2"
    )

# ⬇️ Custom Server für GET-Anfrage von UptimeRobot
class CustomWebhookServer(WebhookServer):
    async def get(self, request):
        return self.response(text="✅ Bot ist online!", status=200)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", getid))

    # Post direkt beim Start prüfen
    import asyncio
    asyncio.get_event_loop().run_until_complete(post_zur_uhrzeit(app.bot))

    # Starte Webhook mit eigener GET-Antwort
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        webhook_server=CustomWebhookServer,
        allowed_updates=["message"]
    )

if __name__ == "__main__":
    main()
