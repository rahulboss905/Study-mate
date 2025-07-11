
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# Import commands implemented in study_tracker.py
from study_tracker import (
    start,
    help_command,
    rec,
    daily,
    leaderboard,
    streak_cmd as streak,
    stats,
)

logging.basicConfig(
    format="%(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app.onrender.com
PORT = int(os.getenv("PORT", "10000"))  # Render supplies PORT env var

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")
if not WEBHOOK_URL:
    raise RuntimeError(
        "WEBHOOK_URL environment variable not set. "
        "Set it to your Render service URL, e.g. https://study-bot.onrender.com"
    )

def build_app():
    """Create the Application and register handlers."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rec", rec))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("streak", streak))
    app.add_handler(CommandHandler("stats", stats))
    return app

if __name__ == "__main__":
    application = build_app()

    logging.info("ðŸ“¡ Starting webhook server on port %s â€¦", PORT)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,  # keeps path secret
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        # You can set 'secret_token' here for extra security (Telegram supports it)
    )
    
