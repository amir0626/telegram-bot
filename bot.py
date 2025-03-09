import os
import json
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Convert admin ID to int
CHANNEL_USERNAME = "aviator_lucky_jet_free_Signals"

# JSON file to store user data
DATA_FILE = "users.json"

# Load user data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {"users": {}}

# Save user data
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Add/update user
def add_user(user_id):
    data = load_data()
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {"joined": str(datetime.datetime.now()), "messages_sent": 0, "subscribed": False}
        save_data(data)

# Start command
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    add_user(user_id)

    keyboard = [
        [InlineKeyboardButton("✅ Subscribe", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("🔄 Check", callback_data="check_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        "👋 *Welcome to Aviator Signal Bot!*\n\n"
        "🚀 *What can this bot do?*\n"
        "✅ 100% accurate signals\n"
        "📢 Daily updates\n"
        "🤖 30,000+ users trust this bot!\n\n"
        "🔄 *After joining, click the 'Check' button below.*\n\n"
        "ℹ️ *Need help?* Use /help"
    )

    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# Subscription check function
async def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        chat_member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)

        if chat_member.status in ["member", "administrator", "creator"]:
            data = load_data()
            data["users"][str(user_id)]["subscribed"] = True
            save_data(data)

            keyboard = [
                [InlineKeyboardButton("🎯 Get Aviator Prediction", callback_data="get_prediction")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.edit_text("✅ You are subscribed! You can now use the bot.", reply_markup=reply_markup)
        else:
            await query.message.edit_text(
                "❌ You have not subscribed yet! Please subscribe first.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Subscribe", url=f"https://t.me/{CHANNEL_USERNAME}")],
                    [InlineKeyboardButton("🔄 Check Again", callback_data="check_subscription")]
                ])
            )
    except Exception:
        await query.message.edit_text(
            "❌ Error checking subscription. Please ensure you joined the channel and try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Subscribe", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("🔄 Check Again", callback_data="check_subscription")]
            ])
        )

# Get Aviator Prediction
async def get_prediction(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    data = load_data()
    if not data["users"].get(str(user_id), {}).get("subscribed", False):
        await query.answer("❌ You need to subscribe first!", show_alert=True)
        return

    prediction_message = (
        "🎰 *FREE AVIATOR PREDICTION! 🎯*\n\n"
        "🚀 *Apni Kismat Badlo!*\n"
        "🔑 *Bas Ek Step Baki Hai!*\n"
        "🎟️ *Game ID Generate Karo Aur Free Prediction Pao!*\n\n"
        "👇 *Generate Game ID* 👇  \n"
        "[🔗 Click Here](https://t.me/+AvrUSyY37D41NzU1)"
    )

    await context.bot.send_message(chat_id=user_id, text=prediction_message, parse_mode="Markdown")

# Help command
async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "🤖 *Need Help?*\n"
        "If you have any questions or issues, feel free to contact the admin.\n\n"
        "👤 *Admin:* @SKRT333\n"
        "📩 [Click here to send a message](https://t.me/SKRT333)"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Admin-only command: Broadcast message
async def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Please provide a message to broadcast.")
        return

    message = " ".join(context.args)
    data = load_data()
    users = data.get("users", {})

    count = 0
    for user_id in users.keys():
        try:
            await context.bot.send_message(chat_id=int(user_id), text=f"📢 Broadcast: {message}")
            count += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Message sent to {count} users.")

# Admin-only command: Show stats
async def stats(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    data = load_data()
    total_users = len(data.get("users", {}))
    await update.message.reply_text(f"📊 Total Users: {total_users}")

# Main function
def main():
    application = Application.builder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    application.add_handler(CallbackQueryHandler(get_prediction, pattern="get_prediction"))

    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
