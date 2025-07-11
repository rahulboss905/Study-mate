
import os
import re
from datetime import datetime
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === ENV Variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))  # 0 = no group restriction; set your group ID to restrict

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set")

# === MongoDB Setup ===
client = MongoClient(MONGO_URI)
db = client["study_bot"]
users = db["users"]

# === Group‑only decorator ===
def group_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # If GROUP_ID is set (non‑zero) enforce group‑only usage
        if GROUP_ID and update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(
                "❌ This bot only works in the official study group."
            )
            return
        return await func(update, context)
    return wrapper

# === /start ===
@group_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Study Bot!\n"
        "Use /rec to log your study time.\n"
        "Type /help to see all commands."
    )

# === /rec ===
@group_only
async def rec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    message = " ".join(context.args)

    if not message:
        await update.message.reply_text(
            "⚠️ Please specify time. Example: `/rec 2hr 30m`",
            parse_mode="Markdown",
        )
        return

    match = re.findall(
        r"(\d+)\s*(hr|h|m|min|minute|minutes)", message, re.IGNORECASE
    )
    total_minutes = 0

    if not match:
        await update.message.reply_text(
            "❌ Invalid format. Try `/rec 2hr 15m` or `/rec 90m`",
            parse_mode="Markdown",
        )
        return

    for value, unit in match:
        value = int(value)
        if unit.lower().startswith("h"):
            total_minutes += value * 60
        elif unit.lower().startswith("m"):
            total_minutes += value

    if total_minutes == 0:
        await update.message.reply_text(
            "❌ Could not understand the time.", parse_mode="Markdown"
        )
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")

    users.update_one(
        {"user_id": user_id},
        {
            "$set": {"name": name},
            "$inc": {f"study_log.{today}": total_minutes, "total_minutes": total_minutes},
        },
        upsert=True,
    )

    await update.message.reply_text(
        f"✅ Recorded {total_minutes} minutes for today. Great job, {name}!"
    )

# === /stats ===
@group_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    today = datetime.utcnow().strftime("%Y-%m-%d")

    user = users.find_one({"user_id": user_id})
    if not user:
        await update.message.reply_text(
            "ℹ️ No study data found. Use /rec to start logging."
        )
        return

    today_minutes = user.get("study_log", {}).get(today, 0)
    total_minutes = user.get("total_minutes", 0)
    streak = user.get("streak", 0)

    await update.message.reply_text(
        f"📊 *{name}'s Stats:*\n\n"
        f"🕒 Today: {today_minutes} min\n"
        f"📈 Total: {total_minutes} min\n"
        f"🔥 Streak: {streak} days",
        parse_mode="Markdown",
    )

# === /daily ===
@group_only
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    results = users.find({f"study_log.{today}": {"$exists": True}})
    leaderboard = [
        (u.get("name", "Unknown"), u["study_log"].get(today, 0)) for u in results
    ]
    leaderboard.sort(key=lambda x: x[1], reverse=True)

    if not leaderboard:
        await update.message.reply_text("📉 No study logs found for today.")
        return

    msg = "*📅 Today's Top Learners:*\n"
    for i, (name, minutes) in enumerate(leaderboard[:10], 1):
        msg += f"{i}. {name} — {minutes} min\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# === /leaderboard ===
@group_only
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = (
        users.find({"total_minutes": {"$gt": 0}})
        .sort("total_minutes", -1)
        .limit(10)
    )
    msg = "*🏆 All‑time Leaderboard:*\n"
    for i, u in enumerate(results, 1):
        msg += f"{i}. {u.get('name', 'Unknown')} — {u.get('total_minutes', 0)} min\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# === /streak ===
@group_only
async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = users.find({"streak": {"$gt": 0}}).sort("streak", -1).limit(10)
    msg = "*🔥 Streak Leaderboard:*\n"
    for i, u in enumerate(results, 1):
        msg += f"{i}. {u.get('name', 'Unknown')} — {u.get('streak', 0)} 🔥\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# === /help ===
@group_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Study Bot Commands Guide:*\n\n"
        "/rec [time] — Log study time\n"
        "/daily — Show today's top learners\n"
        "/leaderboard — Total leaderboard\n"
        "/streak — Streak leaderboard\n"
        "/stats — View your stats\n"
        "/help — Show this help",
        parse_mode="Markdown",
    )

# === MAIN ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rec", rec))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("streak", streak))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()
            
