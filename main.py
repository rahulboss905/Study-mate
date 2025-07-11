import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from study_tracker import start


logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("rec", rec))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("streak", streak))
    app.add_handler(CommandHandler("setweekly", setweekly))
    app.add_handler(CommandHandler("progressw", progressw))
    app.add_handler(CommandHandler("deletew", deletew))
    app.add_handler(CommandHandler("setdaily", setdaily))
    app.add_handler(CommandHandler("progressd", progressd))
    app.add_handler(CommandHandler("deleted", deleted))
    app.add_handler(CommandHandler("update", update))
    app.add_handler(CommandHandler("debt", debt))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("delete", delete_time))
    app.add_handler(CommandHandler("reset", reset))

    print("✅ Bot is running...")
    app.run_polling()
