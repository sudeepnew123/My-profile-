from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes
from datetime import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

user_data = {}  # user_id: (name, username)

# Save user to file
def save_user(user_id, name, username):
    line = f"{user_id} | {name} | @{username if username else 'No Username'}\n"
    if not os.path.exists("users.txt") or line not in open("users.txt").read():
        with open("users.txt", "a") as f:
            f.write(line)

# Log messages
def log_message(user_id, name, username, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} | {user_id} | {name} | @{username if username else 'No Username'} | {message}\n"
    with open("messages.txt", "a") as f:
        f.write(log_line)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = update.message.from_user

    if chat_id != ADMIN_ID:
        name = user.full_name
        username = user.username
        user_data[chat_id] = (name, username)
        save_user(chat_id, name, username)

        # Forward message to admin with clean format
        username_text = f"@{username}" if username else "No Username"
        forward_text = (
            f"**New Message from:**\n"
            f"Name: {name}\n"
            f"Username: {username_text}\n"
            f"User ID: `{chat_id}`\n\n"
            f"**Message:**\n{update.message.text}"
        )

        log_message(chat_id, name, username, update.message.text)

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
    reply_text = " ".join(args[1:])

    # Find user_id if username is given
    if target.startswith("@"):
        uid = None
        for user_id, (_, uname) in user_data.items():
            if uname == target[1:]:
                uid = user_id
                break
        if not uid:
            await update.message.reply_text("Username not found in recent users.")
            return
    else:
        try:
            uid = int(target)
        except:
            await update.message.reply_text("Invalid user_id.")
            return

    try:
        await context.bot.send_message(chat_id=uid, text=reply_text)
        await update.message.reply_text("Replied successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send message: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.add_handler(CommandHandler("reply", reply_command))

app.run_polling()
