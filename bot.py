import os
import traceback
from fastapi import FastAPI
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ✅ Telegram-Bot initialisieren
bot = Bot(token=BOT_TOKEN)

# ✅ FastAPI App
app = FastAPI()

@app.get("/")
async def home():
    return {"status": "✅ App läuft", "bot_token": bool(BOT_TOKEN), "chat_id": CHAT_ID}


@app.get("/trigger")
async def trigger_post():
    try:
        # ✅ Testnachricht senden
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🚀 Testnachricht vom Bot!",
            parse_mode=ParseMode.HTML
        )
        return {"status": "✅ Nachricht erfolgreich gesendet"}
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print("❌ Fehler beim Senden:\n", error_trace)
        return {
            "status": "❌ Fehler beim Senden",
            "fehler": str(e),
            "trace": error_trace
        }
