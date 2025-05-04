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
            "gameid": "",
            "last_message_id": None,
            "language": "hi",  # Default to Hinglish
            "language_selected": False  # Track if language is selected
        }
        save_data(data)

async def delete_previous_message(context: CallbackContext, user_id: int):
    data = load_data()
    user_data = data["users"].get(str(user_id), {})
    last_message_id = user_data.get("last_message_id")
    if last_message_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=last_message_id)
        except Exception:
            pass  # Ignore if message can't be deleted
    return data, user_data

async def update_last_message_id(user_id: int, message_id: int):
    data = load_data()
    if str(user_id) in data["users"]:
        data["users"][str(user_id)]["last_message_id"] = message_id
        save_data(data)

# --- Message Helper Function ---
def get_message(message_key: str, language: str):
    messages = {
        "language_selection": {
            "hi": (
                "🌟 *Language Choose Karo!* 🌟\n\n"
                "Apni pasandida bhasha select karo:\n\n"
                "🇮🇳 Hindi | 🇬🇧 English"
            ),
            "en": (
                "🌟 *Choose Your Language!* 🌟\n\n"
                "Select your preferred language:\n\n"
                "🇮🇳 Hindi | 🇬🇧 English"
            )
        },
        "language_changed": {
            "hi": (
                "✅ *Language Hindi mein set ho gaya!* ✅\n\n"
                "🚀 Ab apni pasandida bhasha mein bot ka maza lo!\n"
                "👇 Main menu par wapas jao:"
            ),
            "en": (
                "✅ *Language set to English!* ✅\n\n"
                "🚀 Enjoy the bot in your preferred language!\n"
                "👇 Return to the main menu:"
            )
        },
        "welcome": {
            "hi": (
                "👋 *Welcome to Aviator Signal Bot!*\n\n"
                "🚀 *Yeh bot kya karta hai?*\n"
                "✅ 100% pakke signals\n"
                "📢 Rozana updates\n"
                "🤖 30,000+ log ispe bharosa karte hain!\n\n"
                "🔄 *Channel join karne ke baad 'Check' button dabao.*\n\n"
                "ℹ️ *Koi help chahiye?* /help use karo"
            ),
            "en": (
                "👋 *Welcome to Aviator Signal Bot!*\n\n"
                "🚀 *What does this bot offer?*\n"
                "✅ 100% accurate signals\n"
                "📢 Daily updates\n"
                "🤖 Trusted by over 30,000 users!\n\n"
                "🔄 *Join our channel and click 'Check' below.*\n\n"
                "ℹ️ *Need assistance?* Use /help"
            )
        },
        "check_success": {
            "hi": (
                "🎉 *Welcome Aboard, Champion!* 🎉\n\n"
                "🚀 *Tum ab hamare exclusive Aviator Signal Bot ke member ho!* \n"
                "💪 *Kya-kya milta hai yaha?*\n"
                "✅ 100% pakke signals\n"
                "📢 Roz ke updates\n"
                "🤖 30,000+ winners ka bharosa\n\n"
                "🔥 *Ab apni jeet ka safar shuru karo!*\n"
                "👇 *Niche buttons se apna next step choose karo!* 👇"
            ),
            "en": (
                "🎉 *Welcome Aboard, Champion!* 🎉\n\n"
                "🚀 *You're now a member of our exclusive Aviator Signal Bot!* \n"
                "💪 *What's in store for you?*\n"
                "✅ 100% accurate signals\n"
                "📢 Daily updates\n"
                "🤖 Trusted by 30,000+ winners\n\n"
                "🔥 *Start your winning journey now!*\n"
                "👇 *Choose your next step below!* 👇"
            )
        },
        "check_fail": {
            "hi": "❌ Tumne abhi channel join nahi kiya! Pehle join karo.",
            "en": "❌ You haven't joined the channel yet! Please join first."
        },
        "check_error": {
            "hi": "❌ Subscription check karne mein error! Channel join karke dobara try karo.",
            "en": "❌ Error checking subscription! Join the channel and try again."
        },
        "get_prediction": {
            "hi": (
                "🎰 *FREE AVIATOR PREDICTION! 🎯*\n\n"
                "🚀 *Apni kismat badlo, bhai!*\n"
                "🔑 *Bas ek step baki hai!*\n"
                "🎟️ *Game ID generate karo aur free prediction pakdo!*\n\n"
                "👇 *Game ID Generate Karne Ke Liye* 👇\n"
                "[🔗 Yaha Click Karo](https://t.me/+157yBHKQqE04NTY1)\n\n"
                "*Abhi Game ID submit karo niche button se!* 👇"
            ),
            "en": (
                "🎰 *FREE AVIATOR PREDICTION!* 🎯\n\n"
                "🚀 *Change your luck today!*\n"
                "🔑 *Just one step away!*\n"
                "🎟️ *Generate your Game ID to grab your free prediction!*\n\n"
                "👇 *To Generate Game ID* 👇\n"
                "[🔗 Click Here](https://t.me/+157yBHKQqE04NTY1)\n\n"
                "*Submit your Game ID using the button below!* 👇"
            )
        },
        "get_signal": {
            "hi": (
                "🎰 *Free Aviator Signals Pakdo, Jeet Shuru Karo!* 🎯\n\n"
                "🚨 *Arre! Tumhara account hamare promo code se nahi bana!* 🚨\n"
                "Regular signals ke liye yeh steps follow karo:\n\n"
                "1️⃣ Naya account banao with *Promo Code*: **VENOM21**\n"
                "2️⃣ Minimum ₹300 deposit karo\n"
                "3️⃣ Game ID submit karo verification ke liye\n\n"
                "🔥 *Par agar 100% pakke VIP Signals chahiye?* Niche VIP Signal button dabao! 🔥\n"
                "👉 [Yaha Click Karo Account Banane Ke Liye](https://t.me/+157yBHKQqE04NTY1)"
            ),
            "en": (
                "🎰 *Unlock Free Aviator Signals & Win Big!* 🎯\n\n"
                "🚨 *Oops! Your account isn’t linked to our promo code!* 🚨\n"
                "To get regular signals, follow these steps:\n\n"
                "1️⃣ Create an account with *Promo Code*: **VENOM21**\n"
                "2️⃣ Deposit a minimum of ₹300\n"
                "3️⃣ Submit your Game ID for verification\n\n"
                "🔥 *Want 100% accurate VIP Signals?* Click the VIP Signal button below! 🔥\n"
                "👉 [Click Here to Create Account](https://t.me/+157yBHKQqE04NTY1)"
            )
        },
        "vip_signal": {
            "hi": (
                "🔥 *VIP Signals Ka Jadoo! 100% Jeet Guarantee!* 🔥\n\n"
                "🚀 *Bhai, VIP Signals ke liye premium plan chahiye!* \n"
                "✅ *Accuracy Rate*: 100% pakka\n"
                "✅ *Exclusive Benefits*: Roz ke top-tier signals\n"
                "✅ *Jeet Ka Shortcut*: Lakho winners ka bharosa!\n\n"
                "📩 *Abhi premium plan ke liye admin se baat karo:*\n"
                "👤 *Admin*: @SKRT333\n\n"
                "👇 *Jaldi se apni jeet unlock karo!* 👇"
            ),
            "en": (
                "🔥 *Unleash the Power of VIP Signals! 100% Win Guarantee!* 🔥\n\n"
                "🚀 *To access VIP Signals, you need our Premium Plan!* \n"
                "✅ *Accuracy Rate*: 100% guaranteed\n"
                "✅ *Exclusive Benefits*: Daily top-tier signals\n"
                "✅ *Shortcut to Victory*: Trusted by thousands of winners!\n\n"
                "📩 *Contact our admin now to get the premium plan:*\n"
                "👤 *Admin*: @SKRT333\n\n"
                "👇 *Unlock your winning streak today!* 👇"
            )
        },
        "send_gameid": {
            "hi": (
                "🎮 Apna Game ID yeh format mein bhejo:\n\n"
                "`/gameid <your_game_id>`\n\n"
                "Example: `/gameid 12345`"
            ),
            "en": (
                "🎮 Please submit your Game ID in this format:\n\n"
                "`/gameid <your_game_id>`\n\n"
                "Example: `/gameid 12345`"
            )
        },
        "gameid_submitted": {
            "hi": "✅ Tumhara Game ID admin ko bhej diya gaya verification ke liye.",
            "en": "✅ Your Game ID has been sent to the admin for verification."
        },
        "gameid_invalid": {
            "hi": "❌ Apna game ID aise bhejo: /gameid <your_game_id>",
            "en": "❌ Please submit your Game ID like this: /gameid <your_game_id>"
        },
        "congratulations": {
            "hi": (
                "🎉 *Congratulations! Tumhara Game ID Accept Ho Gaya!* 🎉\n\n"
                "🚀 *Ab tum 100% pakke Aviator predictions le sakte ho!* \n"
                "📩 Predictions ke liye yaha message karo: 👇\n"
                "👤 *Admin*: @SKRT333\n\n"
                "🔥 *Jeet ka safar shuru karo, bhai!* 🔥"
            ),
            "en": (
                "🎉 *Congratulations! Your Game ID Has Been Approved!* 🎉\n\n"
                "🚀 *You’re now eligible for 100% accurate Aviator predictions!* \n"
                "📩 To get predictions, message here: 👇\n"
                "👤 *Admin*: @SKRT333\n\n"
                "🔥 *Start your winning streak today!* 🔥"
            )
        },
        "reject_gameid": {
            "hi": (
                "🚫 *Oops! Tumhara Game ID Reject Ho Gaya!* 🚫\n\n"
                "🔍 *Kyun?* Tumhara account hamare exclusive promo code se nahi bana! \n"
                "💥 *No tension, bhai!* Abhi account banao aur jeet ka maza lo! \n\n"
                "📋 *Steps to Success:*\n"
                "1️⃣ Naya account banao with *Promo Code*: **VENOM21**\n"
                "2️⃣ Minimum ₹300 deposit karo\n"
                "3️⃣ Game ID submit karo verification ke liye\n\n"
                "🔥 *Abhi shuru karo, lakho winners ke saath judo!* 🔥\n"
                "👉 [Yaha Click Karo Account Banane Ke Liye](https://t.me/+157yBHKQqE04NTY1)"
            ),
            "en": (
                "🚫 *Oops! Your Game ID Has Been Rejected!* 🚫\n\n"
                "🔍 *Why?* Your account wasn’t created with our exclusive promo code! \n"
                "💥 *No worries!* Create an account now and start winning! \n\n"
                "📋 *Steps to Success:*\n"
                "1️⃣ Create an account with *Promo Code*: **VENOM21**\n"
                "2️⃣ Deposit a minimum of ₹300\n"
                "3️⃣ Submit your Game ID for verification\n\n"
                "🔥 *Get started now and join thousands of winners!* 🔥\n"
                "👉 [Click Here to Create Account](https://t.me/+157yBHKQqE04NTY1)"
            )
        },
        "help": {
            "hi": (
                "🤖 *Help chahiye?*\n"
                "Koi bhi sawal ya problem ho, admin se baat karo.\n\n"
                "👤 *Admin:* @SKRT333\n"
                "📩 [Yaha click karke message bhejo](https://t.me/SKRT333)"
            ),
            "en": (
                "🤖 *Need Help?*\n"
                "For any questions or issues, contact our admin.\n\n"
                "👤 *Admin:* @SKRT333\n"
                "📩 [Click here to send a message](https://t.me/SKRT333)"
            )
        }
    }
    return messages.get(message_key, {}).get(language, messages[message_key]["hi"])

# --- Bot Commands ---

# /start command: Adds user and sends language selection or welcome message
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    add_user(user_id)
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")
    
    # Check if language is already selected
    if not user_data.get("language_selected", False):
        keyboard = [
            [
                InlineKeyboardButton("🇮🇳 Hindi", callback_data="select_language_hi"),
                InlineKeyboardButton("🇬🇧 English", callback_data="select_language_en")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.message.reply_text(
            get_message("language_selection", language), 
            reply_markup=reply_markup, 
            parse_mode="Markdown"
        )
        await update_last_message_id(user_id, message.message_id)
        return
    
    # Show welcome message if language is already selected
    keyboard = [
        [InlineKeyboardButton("✅ Subscribe", url="https://t.me/+157yBHKQqE04NTY1")],
        [InlineKeyboardButton("🔄 Check", callback_data="check_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text(
        get_message("welcome", language), 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )
    await update_last_message_id(user_id, message.message_id)

# /select_language callback: Set language and show welcome message (for /start)
async def select_language(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    
    # Set language based on callback data
    language = "hi" if query.data == "select_language_hi" else "en"
    data["users"][str(user_id)]["language"] = language
    data["users"][str(user_id)]["language_selected"] = True
    save_data(data)
    
    # Show welcome message
    keyboard = [
        [InlineKeyboardButton("✅ Subscribe", url="https://t.me/+157yBHKQqE04NTY1")],
        [InlineKeyboardButton("🔄 Check", callback_data="check_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await query.message.reply_text(
        get_message("welcome", language), 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )
    await update_last_message_id(user_id, message.message_id)

# /check_subscription callback: Check if user has joined channel
async def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")
    
    try:
        chat_member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            data["users"][str(user_id)]["subscribed"] = True
            save_data(data)
            keyboard = [
                [
                    InlineKeyboardButton("✨ Register Now", callback_data="get_prediction"),
                    InlineKeyboardButton("🆕 Submit Game ID", callback_data="send_gameid")
                ],
                [
                    InlineKeyboardButton("🎯 Get Signal", callback_data="get_signal"),
                    InlineKeyboardButton("🌐 Change Language", callback_data="change_language")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await query.message.reply_text(
                get_message("check_success", language), 
                reply_markup=reply_markup, 
                parse_mode="Markdown"
            )
            await update_last_message_id(user_id, message.message_id)
        else:
            keyboard = [
                [InlineKeyboardButton("✅ Subscribe", url="https://t.me/+157yBHKQqE04NTY1")],
                [InlineKeyboardButton("🔄 Check Again", callback_data="check_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await query.message.reply_text(
                get_message("check_fail", language), 
                reply_markup=reply_markup, 
                parse_mode="Markdown"
            )
            await update_last_message_id(user_id, message.message_id)
    except Exception:
        keyboard = [
            [InlineKeyboardButton("✅ Subscribe", url="https://t.me/+157yBHKQqE04NTY1")],
            [InlineKeyboardButton("🔄 Check Again", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await query.message.reply_text(
            get_message("check_error", language), 
            reply_markup=reply_markup, 
            parse_mode="Markdown"
        )
        await update_last_message_id(user_id, message.message_id)

# /change_language callback: Show language selection options
async def change_language(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")
    
    # Show language selection options
    keyboard = [
        [
            InlineKeyboardButton("🇮🇳 Hindi", callback_data="confirm_language_hi"),
            InlineKeyboardButton("🇬🇧 English", callback_data="confirm_language_en")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await query.message.reply_text(
        get_message("language_selection", language), 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )
    await update_last_message_id(user_id, message.message_id)

# /confirm_language callback: Confirm language change and show confirmation
async def confirm_language(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    
    # Set language based on callback data
    language = "hi" if query.data == "confirm_language_hi" else "en"
    data["users"][str(user_id)]["language"] = language
    save_data(data)
    
    # Show confirmation message with back to main menu button
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await query.message.reply_text(
        get_message("language_changed", language), 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )
    await update_last_message_id(user_id, message.message_id)

# /get_prediction callback: Sends prediction message with a button/link
async def get_prediction(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")

    if not user_data.get("subscribed", False):
        await query.answer("❌ Pehle channel join karo!" if language == "hi" else "❌ Join the channel first!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("🆕 Submit Game ID", callback_data="send_gameid")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.send_message(
        chat_id=user_id, 
        text=get_message("get_prediction", language), 
        parse_mode="Markdown", 
        reply_markup=reply_markup
    )
    await update_last_message_id(user_id, message.message_id)

# /get_signal callback: Sends message with VIP and back buttons
async def get_signal(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")

    keyboard = [
        [InlineKeyboardButton("🔥 VIP Signal", callback_data="vip_signal")],
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.send_message(
        chat_id=user_id, 
        text=get_message("get_signal", language), 
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    await update_last_message_id(user_id, message.message_id)

# /vip_signal callback: Sends premium VIP signal message
async def vip_signal(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")

    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.send_message(
        chat_id=user_id, 
        text=get_message("vip_signal", language), 
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    await update_last_message_id(user_id, message.message_id)

# /send_gameid callback: Prompt user to send their game ID
async def send_gameid(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")

    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await query.message.reply_text(
        get_message("send_gameid", language), 
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    await update_last_message_id(user_id, message.message_id)

# /gameid command: User sends their game id for verification
async def gameid_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")

    if len(context.args) < 1:
        keyboard = [
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.message.reply_text(
            get_message("gameid_invalid", language),
            reply_markup=reply_markup
        )
        await update_last_message_id(user_id, message.message_id)
        return
    game_id = " ".join(context.args)
    
    # Save game id in user data
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
    
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text(
        get_message("gameid_submitted", language),
        reply_markup=reply_markup
    )
    await update_last_message_id(user_id, message.message_id)

# /back_to_main_menu callback: Return to main menu
async def back_to_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")
    
    if not user_data.get("subscribed", False):
        keyboard = [
            [InlineKeyboardButton("✅ Subscribe", url="https://t.me/+157yBHKQqE04NTY1")],
            [InlineKeyboardButton("🔄 Check", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await query.message.reply_text(
            get_message("welcome", language), 
            reply_markup=reply_markup, 
            parse_mode="Markdown"
        )
        await update_last_message_id(user_id, message.message_id)
        return
    
    keyboard = [
        [
            InlineKeyboardButton("✨ Register Now", callback_data="get_prediction"),
            InlineKeyboardButton("🆕 Submit Game ID", callback_data="send_gameid")
        ],
        [
            InlineKeyboardButton("🎯 Get Signal", callback_data="get_signal"),
            InlineKeyboardButton("🌐 Change Language", callback_data="change_language")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await query.message.reply_text(
        get_message("check_success", language), 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )
    await update_last_message_id(user_id, message.message_id)

# Callback for Accepting Game ID (Admin)
async def accept_gameid(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    # Parse user id from callback data, format: "accept_gameid_{user_id}"
    parts = query.data.split("_")
    if len(parts) < 3:
        return
    target_user_id = parts[2]
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, int(target_user_id))
    language = user_data.get("language", "hi")
    
    # Send congratulations message
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.send_message(
        chat_id=int(target_user_id), 
        text=get_message("congratulations", language), 
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    await update_last_message_id(int(target_user_id), message.message_id)
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
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, int(target_user_id))
    language = user_data.get("language", "hi")
    
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.send_message(
        chat_id=int(target_user_id), 
        text=get_message("reject_gameid", language), 
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    await update_last_message_id(int(target_user_id), message.message_id)
    await query.edit_message_text("Game ID rejected.")

# /help command
async def help_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    # Delete previous message
    data, user_data = await delete_previous_message(context, user_id)
    language = user_data.get("language", "hi")
    
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text(
        get_message("help", language),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    await update_last_message_id(user_id, message.message_id)

# Admin-only command: Broadcast message
async def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ Broadcast ke liye message bhejo.")
        return
    message = " ".join(context.args)
    data = load_data()
    users = data.get("users", {})
    count = 0
    for uid in users.keys():
        try:
            # Delete previous message for each user
            await delete_previous_message(context, int(uid))
            sent_message = await context.bot.send_message(
                chat_id=int(uid), 
                text=f"📢 Broadcast: {message}"
            )
            await update_last_message_id(int(uid), sent_message.message_id)
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Message {count} users ko bhej diya.")

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

    # Callback Query Handlers
    application.add_handler(CallbackQueryHandler(select_language, pattern="select_language_"))
    application.add_handler(CallbackQueryHandler(confirm_language, pattern="confirm_language_"))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    application.add_handler(CallbackQueryHandler(change_language, pattern="change_language"))
    application.add_handler(CallbackQueryHandler(get_prediction, pattern="get_prediction"))
    application.add_handler(CallbackQueryHandler(get_signal, pattern="get_signal"))
    application.add_handler(CallbackQueryHandler(vip_signal, pattern="vip_signal"))
    application.add_handler(CallbackQueryHandler(send_gameid, pattern="send_gameid"))
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="back_to_main_menu"))
    application.add_handler(CallbackQueryHandler(accept_gameid, pattern="accept_gameid_"))
    application.add_handler(CallbackQueryHandler(reject_gameid, pattern="reject_gameid_"))

    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
