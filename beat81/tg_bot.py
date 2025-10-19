import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Application, ContextTypes, filters

from beat81 import login, tickets, event_info, ticket_info
from date_helper import get_date_formatted_short
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
        keyboard = main_menu()
    else:
        keyboard = [[InlineKeyboardButton("Login", callback_data="login")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with Inline Keyboard
    await update.message.reply_text("Choose an option below:", reply_markup=reply_markup)


# Callback for handling button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Answer the callback query

    telegram_user_id = query.from_user.id

    if query.data == "main_menu":
        await query.message.reply_text("Choose an option below:", reply_markup=InlineKeyboardMarkup(main_menu()))

    if query.data == "login":
        # Start the login process by asking for the email
        await query.message.reply_text("Please enter your email:")
        user_data[telegram_user_id] = {"step": "email"}  # Track the next step for this user

    elif query.data == "get_my_bookings" or query.data == "cancelTicket_back":
        tickets_response = tickets(telegram_user_id)
        keyboard = []
        for ticket in tickets_response.get('data', []):
            event = ticket.get('event')
            iso_date = event.get('date_begin')
            formatted_time = get_date_formatted_short(iso_date)
            location = event.get('location')
            location_name = location.get('name')
            ticket_id = ticket.get('id')
            keyboard.append(
                [InlineKeyboardButton(f"{location_name} - {formatted_time}",
                                      callback_data=f"ticketInfo_{ticket_id}")])
        keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"Total bookings: {tickets_response.get('total')}", reply_markup=reply_markup)

    elif query.data.startswith("cancelTicket_"):
        ticket_id = query.data.split("_")[1]
        await query.message.reply_text(f"Ticket {ticket_id} cancelled successfully")

    elif query.data.startswith("ticketInfo_"):
        ticket_id = query.data.split("_")[1]
        ticket = ticket_info(telegram_user_id, ticket_id).get('data')
        event = ticket.get('event')
        iso_date = event.get('date_begin')
        formatted_time = get_date_formatted_short(iso_date)
        location = event.get('location')
        location_name = location.get('name')
        max_participants = event.get('max_participants')
        participants_count = event.get('participants_count')
        address = location.get('address')
        complete_address = f"{address.get('address1')}, {address.get('zip')}"
        keyboard = [[InlineKeyboardButton("Cancel", callback_data=f"cancelTicket_{ticket_id}")],
                    [InlineKeyboardButton("Back", callback_data="cancelTicket_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"Participants: {participants_count}/{max_participants}\nPlace: {location_name}\nAddress:{complete_address}\nDate: {formatted_time}",
            reply_markup=reply_markup)


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


def main_menu():
    return [[InlineKeyboardButton("Get my bookings", callback_data="get_my_bookings")]]


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
