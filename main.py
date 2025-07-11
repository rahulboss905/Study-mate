
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# Import your command handlers from study_tracker.py
from study_tracker import (
    start,
    help_command,
    rec,
    daily,
    leaderboard,
    streak_cmd as streak,
    stats,
)

# === Configuration ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", "10000"))  # Render sets PORT automatically

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")
if not WEBHOOK_URL:
    raise RuntimeError(
        "Neither WEBHOOK_URL nor RENDER_EXTERNAL_URL is set. "
        "Set one of them in Render â†’ Environment."
    )

logging.basicConfig(
    format="%(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
)

def build_app():
    """Create the Application and register all command handlers."""
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

    logging.info("ðŸ“¡ Starting webhook server on port %%s â€¦", PORT)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,               # keeps the path private
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",  # Telegram endpoint
        # secret_token="OPTIONAL-SECRET",  # enable for extra security
    )
    
