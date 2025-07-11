
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# Import commands from study_tracker.py
from study_tracker import (
    start,
    help_command,
    rec,
    daily,
    leaderboard,
    streak,
    stats,
)

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rec", rec))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("streak", streak))
    app.add_handler(CommandHandler("stats", stats))

    logging.info("✅ Bot is running...")
    app.run_polling()
    
