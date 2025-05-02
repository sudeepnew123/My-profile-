from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

user_map = {}

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_map[user.id] = user.username or user.first_name
    msg = f"From @{user.username or user.first_name} (ID: {user.id}):\n{update.message.text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split(" ", 2)
        target_id = int(parts[1])
        reply_text = parts[2]
        await context.bot.send_message(chat_id=target_id, text=f"Admin:\n{reply_text}")
    except:
        await update.message.reply_text("Usage: /reply <user_id> <message>")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
app.add_handler(CommandHandler("reply", reply_command))

app.run_polling()
