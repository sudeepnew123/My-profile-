from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Store user chat IDs only
user_ids = set()

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_ids.add(update.message.chat_id)
    await context.bot.send_message(chat_id=ADMIN_ID, text=update.message.text)

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split(" ", 2)
        target_id = int(parts[1])
        msg = parts[2]
        await context.bot.send_message(chat_id=target_id, text=msg)
    except:
        await update.message.reply_text("Use like: /reply <user_id> <message>")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
app.add_handler(CommandHandler("reply", reply_command))

app.run_polling()
