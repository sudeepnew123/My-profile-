from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

user_ids = set()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_ids
    chat_id = update.message.chat_id

    if chat_id != ADMIN_ID:
        user_ids.add(chat_id)
        # Check if message is a sticker
        if update.message.sticker:
            await context.bot.send_sticker(chat_id=ADMIN_ID, sticker=update.message.sticker.file_id)
        # Check if message is text
        elif update.message.text:
            await context.bot.send_message(chat_id=ADMIN_ID, text=update.message.text)
    else:
        failed = 0
        for uid in user_ids:
            try:
                await context.bot.send_chat_action(chat_id=uid, action="typing")
                # If it's a sticker, send it
                if update.message.sticker:
                    await context.bot.send_sticker(chat_id=uid, sticker=update.message.sticker.file_id)
                # If it's a text message, send it
                elif update.message.text:
                    await context.bot.send_message(chat_id=uid, text=update.message.text)
            except:
                failed += 1
        await update.message.reply_text(f"Sent to {len(user_ids)-failed} users, failed: {failed}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(MessageHandler(filters.STICKER, handle_message))  # Added sticker filter separately

app.run_polling()
