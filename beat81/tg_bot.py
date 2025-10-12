import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Application, ContextTypes, filters
from dotenv import load_dotenv
from beat81 import login, tickets
from db_helper import get_user_by_user_id

# Load token and other environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TG_TOKEN")  # This should match the key in your .env file

# Dictionary to hold user data temporarily
user_data = {}


# Start command: Show a menu with options (like the Login button)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create a keyboard with a "Login" button
    user_id = update.effective_user.id
    user = get_user_by_user_id(str(user_id))
    if user:
        keyboard = [[InlineKeyboardButton("Get my bookings", callback_data="get_my_bookings")]]
    else:
        keyboard = [[InlineKeyboardButton("Login", callback_data="login")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with Inline Keyboard
    await update.message.reply_text("Choose an option below:", reply_markup=reply_markup)

# Callback for handling button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Answer the callback query

    if query.data == "login":
        # Start the login process by asking for the email
        await query.message.reply_text("Please enter your email:")
        user_data[query.from_user.id] = {"step": "email"}  # Track the next step for this user

    if query.data == "get_my_bookings":
        tickets_response = tickets(query.from_user.id)
        await query.message.reply_text(f"Total bookings: {tickets_response}")


# Message handler for email and password input
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check if the user is in the middle of the login process
    if user_id in user_data:
        step = user_data[user_id].get("step")

        if step == "email":
            # Save the email so we can ask for the password next
            user_data[user_id]["email"] = update.message.text
            user_data[user_id]["step"] = "password"

            await update.message.reply_text("Got it! Now enter your password:")

        elif step == "password":
            # Save the password and call the login API
            user_data[user_id]["password"] = update.message.text
            email = user_data[user_id]["email"]
            password = user_data[user_id]["password"]

            # Call the login API
            login_success = login(user_id, email, password)

            if login_success:
                await update.message.reply_text("Login successful! 🎉")
            else:
                await update.message.reply_text("Login failed. Please try again.")

            # Clear user data after login attempt
            del user_data[user_id]

    else:
        await update.message.reply_text("Please click on the Login button to start the process.")



# Main function to run the bot
if __name__ == "__main__":
    # Ensure the bot token was loaded correctly
    if not BOT_TOKEN:
        print("Error: Bot token not found in environment variables!")
        exit(1)

    # Build the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add Command and Callback handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Start the bot
    application.run_polling()
