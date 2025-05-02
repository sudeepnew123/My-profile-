from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import os

# Fetching environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# In-memory user data storage
user_data = {}  # user_id: (name, username)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = update.message.from_user

    if chat_id != ADMIN_ID:
        # Save user info
        name = user.full_name
        username = user.username
        user_data[chat_id] = (name, username)

        uname_display = f"@{username}" if username else "No username"
        forward_text = f"**From:** {name} ({uname_display})\n**User ID:** `{chat_id}`\n\n**Message:**\n{update.message.text}"

        # Send message to admin
        await context.bot.send_message(chat_id=ADMIN_ID, text=forward_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("Use /reply <user_id or @username> <message> to respond.")

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /reply <user_id or @username> <message>")
        return

    target = args[0]
    message = " ".join(args[1:])

    # Finding the user_id from username or directly using the provided user_id
    uid = None
    if target.startswith("@"):
        # Lookup username
        for user_id, (_, uname) in user_data.items():
            if uname == target[1:]:
                uid = user_id
                break
        if uid is None:
            await update.message.reply_text("Username not found.")
            return
    else:
        try:
            uid = int(target)
        except ValueError:
            await update.message.reply_text("Invalid user_id.")
            return

    try:
        await context.bot.send_message(chat_id=uid, text=message)
        await update.message.reply_text("Message sent successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send: {e}")

# Initialize the bot application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add handlers
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.add_handler(CommandHandler("reply", reply_command))

# Start polling
app.run_polling()
