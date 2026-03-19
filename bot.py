import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 SECURE ENV VARIABLES
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not set in environment variables")

users = set()

logging.basicConfig(level=logging.INFO)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)

    await update.message.reply_text(
        "🔥 Welcome to Image Generator Bot!\n\n"
        "Send:\n"
        "/generate a king sitting on throne\n\n"
        "I will create AI image for you."
    )

# GENERATE IMAGE
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)

    if not context.args:
        await update.message.reply_text("❌ Usage:\n/generate your prompt")
        return

    prompt = " ".join(context.args)

    await update.message.reply_text("🎨 Generating image...")

    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}"

        response = requests.get(url, timeout=60)

        if response.status_code == 200:
            await update.message.reply_photo(photo=response.content)
        else:
            await update.message.reply_text("❌ Failed to generate image.")

    except Exception as e:
        logging.error(e)
        await update.message.reply_text("⚠️ Error occurred.")

# STATS (ADMIN ONLY)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(f"👥 Total Users: {len(users)}")

# BROADCAST (ADMIN ONLY)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage:\n/broadcast message")
        return

    message = " ".join(context.args)

    success = 0

    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text=message)
            success += 1
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {success} users")

# MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("✅ Bot Running Securely...")
    app.run_polling()
