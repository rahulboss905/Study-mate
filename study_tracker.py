import os
from telegram import Update
from telegram.ext import ContextTypes
from pymongo import MongoClient

GROUP_ID = -1002735734448  # 🔁 Replace with your actual group ID

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["study_bot"]
users = db["users"]

def group_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text("❌ This bot only works in the official study group.")
            return
        return await func(update, context)
    return wrapper

@group_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 Welcome to Study Bot! Use /rec [time] to log your study.")

@group_only
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Study Bot Commands Guide:*\n\n"
        "/rec [time] — Log study time\n"
        "/daily — Show today's top learners\n"
        "/weekly — Weekly leaderboard\n"
        "/leaderboard — Total leaderboard\n"
        "/streak — Streak leaderboard\n"
        "/setweekly [time] — Set weekly goal\n"
        "/progressw — Weekly goal progress\n"
        "/deletew — Delete weekly goal\n"
        "/setdaily [time] — Set daily goal\n"
        "/progressd — Daily goal progress\n"
        "/deleted — Delete daily goal\n"
        "/debt [time] [date] — Pay debt\n"
        "/update — Update debt info\n"
        "/stats — View your stats\n"
        "/delete [time] — Remove logged time\n"
        "/reset — Reset all data\n"
        "/help — Show this help", parse_mode="Markdown"
    )

# Placeholders — real logic can later use MongoDB
@group_only
async def rec(update, context): await update.message.reply_text("✅ Study time recorded!")
@group_only
async def daily(update, context): await update.message.reply_text("📊 Today's top learners.")
@group_only
async def weekly(update, context): await update.message.reply_text("📈 Weekly top learners.")
@group_only
async def leaderboard(update, context): await update.message.reply_text("🏆 All-time leaderboard.")
@group_only
async def streak(update, context): await update.message.reply_text("🔥 Streak leaderboard.")
@group_only
async def setweekly(update, context): await update.message.reply_text("📅 Weekly goal set!")
@group_only
async def progressw(update, context): await update.message.reply_text("📊 Weekly progress.")
@group_only
async def deletew(update, context): await update.message.reply_text("🧹 Weekly goal deleted.")
@group_only
async def setdaily(update, context): await update.message.reply_text("📆 Daily goal set!")
@group_only
async def progressd(update, context): await update.message.reply_text("📊 Daily progress.")
@group_only
async def deleted(update, context): await update.message.reply_text("🧹 Daily goal deleted.")
@group_only
async def update(update, context): await update.message.reply_text("🔄 Study debt updated.")
@group_only
async def debt(update, context): await update.message.reply_text("💰 Debt paid.")
@group_only
async def stats(update, context): await update.message.reply_text("📈 Stats overview.")
@group_only
async def delete_time(update, context): await update.message.reply_text("🗑️ Time deleted.")
@group_only
async def reset(update, context): await update.message.reply_text("❌ All data reset.")
