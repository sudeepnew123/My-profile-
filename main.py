import os
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from collections import defaultdict
import logging

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Logging (optional for Render debug)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Memory to store messages with IDs
message_db = {}
message_counter = 1  # auto-increment ID

# Detect group messages mentioning/replying to bot
async def group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_counter

    if update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
        pass  # bot was replied to
    elif context.bot.username.lower() in update.message.text.lower():
        pass  # bot was tagged
    else:
        return  # not for bot

    user = update.message.from_user
    chat_id = update.message.chat_id
    msg_id = update.message.message_id
    text = update.message.text

    # Save the reference with unique ID
    global message_db
    message_db[str(message_counter)] = {
        "user_id": user.id,
        "chat_id": chat_id,
        "msg_id": msg_id,
        "name": user.full_name,
        "username": user.username or "NoUsername"
    }

    msg_text = f"ID - {message_counter}\nName: {user.full_name} (@{user.username or 'NoUsername'})\nMessage: {text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg_text)
    message_counter += 1

# Handle text or sticker in private (from admin)
async def private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        if update.message.sticker:
            await update.message.reply_text("Sticker nahi, message bhejo.")
        elif update.message.text:
            user = update.message.from_user
            msg_text = f"Name: {user.full_name} (@{user.username or 'NoUsername'})\nMessage: {update.message.text}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg_text)
        return

# Command to reply: /y <id> <message>
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Format: /y <id> <message>")
        return

    msg_id = args[0]
    reply_text = " ".join(args[1:])

    if msg_id not in message_db:
        await update.message.reply_text("Invalid ID.")
        return

    data = message_db[msg_id]
    try:
        await context.bot.send_chat_action(chat_id=data['chat_id'], action=ChatAction.TYPING)
        await context.bot.send_message(chat_id=data['chat_id'], text=reply_text, reply_to_message_id=data['msg_id'])
        await update.message.reply_text("Message sent.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send: {e}")

# Register handlers
app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, group_message))
app.add_handler(MessageHandler(filters.ChatType.PRIVATE & (filters.TEXT | filters.Sticker), private_message))
app.add_handler(CommandHandler("y", reply_command))

# Default route for Render
@app.route("/")
def home():
    return "Bot is running!"

# Start the bot
if __name__ == "__main__":
    app.run_polling()
