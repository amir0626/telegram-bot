import os
import json
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Ensure admin ID is an integer
CHANNEL_USERNAME = "aviator_lucky_jet_free_Signals"

# File to store user data
DATA_FILE = "users.json"

# --- User Data Functions ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def add_user(user_id):
    data = load_data()
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
            "joined": str(datetime.datetime.now()),
            "messages_sent": 0,
            "subscribed": False,
            "gameid": ""
        }
        save_data(data)

# --- Bot Commands ---

# /start command: Adds user and sends welcome message with inline buttons
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    add_user(user_id)
    
    # Check subscription later via Check button.
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

# /check_subscription callback: Check if user has joined channel
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
                [InlineKeyboardButton("🎯 Get Aviator Prediction", callback_data="get_prediction")],
                [InlineKeyboardButton("🆕 Send Game ID", callback_data="send_gameid")]  # New button for sending game id
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

# /get_prediction callback: Sends prediction message with a button/link
async def get_prediction(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Acknowledge callback immediately
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
        "👇 *Generate Game ID* 👇\n"
        "[🔗 Click Here](https://t.me/+157yBHKQqE04NTY1)"
    )
    await context.bot.send_message(chat_id=user_id, text=prediction_message, parse_mode="Markdown")

# /send_gameid callback: Prompt user to send their game ID
async def send_gameid(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    # Prompt the user to send their game ID
    await query.message.reply_text("🎮 Please send your Game ID using the following format:\n\n`/gameid <your_game_id>`\n\nExample: `/gameid 12345`", parse_mode="Markdown")

# /gameid command: User sends their game id for verification
async def gameid_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if len(context.args) < 1:
        await update.message.reply_text("❌ Please send your game id using: /gameid <your_game_id>")
        return
    game_id = " ".join(context.args)
    data = load_data()
    # Save game id in user data
    if str(user_id) in data["users"]:
        data["users"][str(user_id)]["gameid"] = game_id
        save_data(data)
    # Forward to admin with inline buttons for verification
    forward_text = (
        "📩 *Game ID Received*\n"
        f"From: @{update.message.from_user.username or update.message.from_user.first_name}\n"
        f"User ID: {user_id}\n"
        f"Game ID: {game_id}"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Accept", callback_data=f"accept_gameid_{user_id}")],
        [InlineKeyboardButton("❌ Reject", callback_data=f"reject_gameid_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=ADMIN_ID, text=forward_text, parse_mode="Markdown", reply_markup=reply_markup)
    await update.message.reply_text("Your game ID has been forwarded to admin for verification.")

# Callback for Accepting Game ID (Admin)
async def accept_gameid(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    # Parse user id from callback data, format: "accept_gameid_{user_id}"
    parts = query.data.split("_")
    if len(parts) < 3:
        return
    target_user_id = parts[2]
    await context.bot.send_message(chat_id=int(target_user_id), text="✅ Your game ID has been accepted!")
    await query.edit_message_text("Game ID accepted.")

# Callback for Rejecting Game ID (Admin)
async def reject_gameid(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    # Parse user id from callback data, format: "reject_gameid_{user_id}"
    parts = query.data.split("_")
    if len(parts) < 3:
        return
    target_user_id = parts[2]
    rejection_message = (
        "🚫 **Aapka account hamare promo code se nahi bana hai!**\n\n"
        "Please create your account using our **Exclusive Promo Code** and deposit a minimum of ₹300 to generate your Game ID.\n\n"
        "Kripya in steps ko follow karein for successful verification. Thank you!"
    )
    await context.bot.send_message(chat_id=int(target_user_id), text=rejection_message, parse_mode="Markdown")
    await query.edit_message_text("Game ID rejected.")

# /help command
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
    for uid in users.keys():
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 Broadcast: {message}")
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

# --- Main function ---
def main():
    application = Application.builder().token(TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("gameid", gameid_command))

    # Callback Query Handlers222
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    application.add_handler(CallbackQueryHandler(get_prediction, pattern="get_prediction"))
    application.add_handler(CallbackQueryHandler(send_gameid, pattern="send_gameid"))  # New handler
    application.add_handler(CallbackQueryHandler(accept_gameid, pattern="accept_gameid_"))
    application.add_handler(CallbackQueryHandler(reject_gameid, pattern="reject_gameid_"))

    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
