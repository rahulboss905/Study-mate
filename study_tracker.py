
from telegram import Update
from telegram.ext import ContextTypes

GROUP_ID = -1002735734448

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
async def rec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Study time recorded!")

@group_only
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Today's top learners.")

@group_only
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Weekly top learners.")

@group_only
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏆 All-time leaderboard.")

@group_only
async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Your current streak.")

@group_only
async def setweekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Weekly goal set!")

@group_only
async def progressw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Weekly progress bar.")

@group_only
async def deletew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧹 Weekly goal deleted.")

@group_only
async def setdaily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📆 Daily goal set!")

@group_only
async def progressd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Daily progress bar with debt info.")

@group_only
async def deleted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧹 Daily goal deleted.")

@group_only
async def update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Debt info updated.")

@group_only
async def debt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Debt paid!")

@group_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Your study stats.")

@group_only
async def delete_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗑️ Logged time removed.")

@group_only
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ All data reset.")
