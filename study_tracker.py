
import os
import re
from datetime import datetime, timedelta
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

if not BOT_TOKEN or not MONGO_URI:
    raise RuntimeError("Environment variables BOT_TOKEN and MONGO_URI must be set")

client = MongoClient(MONGO_URI)
db = client["study_bot"]
users = db["users"]

def group_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if GROUP_ID and update.effective_chat.id != GROUP_ID:
            await update.message.reply_text("❌ This bot only works in the official study group.")
            return
        return await func(update, context)
    return wrapper

@group_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Study Bot!\n"
        "Use /rec to log your study time.\n"
        "Type /help to see all commands."
    )

@group_only
async def rec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log study time and show detailed progress."""
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    message = " ".join(context.args)

    if not message:
        await update.message.reply_text(
            "⚠️ Please specify time. Example: `/rec 2h 30m`",
            parse_mode="Markdown",
        )
        return

    # Parse minutes
    match = re.findall(r"(\d+)\s*(hr|h|m|min|minute|minutes)", message, re.IGNORECASE)
    total_minutes_logged = 0
    for value, unit in match:
        value = int(value)
        if unit.lower().startswith("h"):
            total_minutes_logged += value * 60
        else:
            total_minutes_logged += value

    if total_minutes_logged == 0:
        await update.message.reply_text("❌ Could not understand the time.", parse_mode="Markdown")
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Fetch current user doc
    user = users.find_one({"user_id": user_id}) or {}
    daily_goal = user.get("daily_goal", 9 * 60)  # default 9 hours = 540 min
    streak = user.get("streak", 0)
    last_date = user.get("last_date")

    # Calculate new streak
    if last_date == today:
        # Already logged today: keep current streak
        pass
    elif last_date == yesterday:
        streak += 1
    else:
        streak = 1  # reset/first day
    # Update study minutes
    users.update_one(
        {"user_id": user_id},
        {
            "$set": {"name": name, "last_date": today, "streak": streak, "daily_goal": daily_goal},
            "$inc": {f"study_log.{today}": total_minutes_logged, "total_minutes": total_minutes_logged},
            "$setOnInsert": {"total_debt": 0},
        },
        upsert=True,
    )

    # Get updated record
    updated = users.find_one({"user_id": user_id})
    today_total = updated.get("study_log", {}).get(today, 0)
    progress_percent = (today_total / daily_goal) * 100 if daily_goal else 0
    remaining_minutes = max(daily_goal - today_total, 0)
    total_debt = updated.get("total_debt", 0)

    # Build response
    msg = (
        f"✅ Logged: {total_minutes_logged} minutes\n"
        f"📆 Today total: {today_total} minutes\n"
        f"🔥 Streak: {streak} days\n\n"
        f"🎯 Daily Goal: {daily_goal // 60}h {daily_goal % 60}m\n"
        f"📊 Progress: {progress_percent:.1f}%\n"
        f"⏰ Remaining: {remaining_minutes // 60}h {remaining_minutes % 60}m\n"
        f"💳 Total Debt: {total_debt // 60}h {total_debt % 60}m"
    )
    await update.message.reply_text(msg)

@group_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    today = datetime.utcnow().strftime("%Y-%m-%d")

    user = users.find_one({"user_id": user_id})
    if not user:
        await update.message.reply_text("ℹ️ No study data found. Use /rec to start logging.")
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

@group_only
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    results = users.find({f"study_log.{today}": {"$exists": True}})
    leaderboard = [(u.get("name", "Unknown"), u["study_log"].get(today, 0)) for u in results]
    leaderboard.sort(key=lambda x: x[1], reverse=True)

    if not leaderboard:
        await update.message.reply_text("📉 No study logs found for today.")
        return

    msg = "*📅 Today's Top Learners:*\n"
    for i, (name, minutes) in enumerate(leaderboard[:10], 1):
        msg += f"{i}. {name} — {minutes} min\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

@group_only
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = users.find({"total_minutes": {"$gt": 0}}).sort("total_minutes", -1).limit(10)
    msg = "*🏆 All‑time Leaderboard:*\n"
    for i, u in enumerate(results, 1):
        msg += f"{i}. {u.get('name', 'Unknown')} — {u.get('total_minutes', 0)} min\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

@group_only
async def streak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = users.find({"streak": {"$gt": 0}}).sort("streak", -1).limit(10)
    msg = "*🔥 Streak Leaderboard:*\n"
    for i, u in enumerate(results, 1):
        msg += f"{i}. {u.get('name', 'Unknown')} — {u.get('streak', 0)} 🔥\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

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

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rec", rec))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("streak", streak_cmd))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()
