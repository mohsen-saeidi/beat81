import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Application, ContextTypes, filters

from beat81.beat81_api import login, tickets, ticket_info, ticket_cancel, UnauthorizedException, events, event_info, \
    register_event, register_series
from beat81.city_helper import City
from beat81.date_helper import get_date_formatted_day_hour, DaysOfWeek, get_date_formatted_hour, get_weekday_form_date
from beat81.db_helper import get_user_by_user_id, clear_token, save_subscription

# Load token and other environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TG_TOKEN")  # This should match the key in your .env file

# Dictionary to hold user data temporarily
user_data = {}


# Start command: Show a menu with options (like the Login button)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Main menu", reply_markup=main_menu_keyboard(update.effective_user.id))


# Callback for handling button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Answer the callback query

    telegram_user_id = query.from_user.id

    if query.data == "main_menu":
        await query.message.reply_text("Main menu", reply_markup=main_menu_keyboard(telegram_user_id))

    if query.data == "login":
        # Start the login process by asking for the email
        await query.message.reply_text("Please enter your email:")
        user_data[telegram_user_id] = {"step": "email"}  # Track the next step for this user

    elif query.data == "get_my_bookings":
        await get_my_bookings(query, telegram_user_id)

    elif query.data.startswith("cancelTicket_"):
        ticket_id = query.data.split("_")[1]
        result = ticket_cancel(telegram_user_id, ticket_id)
        if result:
            await query.message.reply_text("Ticket cancelled successfully")
        else:
            await query.message.reply_text(f"Could not cancel ticket. Please try again later.")
        await get_my_bookings(query, telegram_user_id)

    elif query.data.startswith("ticketInfo_"):
        ticket_id = query.data.split("_")[1]
        ticket = ticket_info(telegram_user_id, ticket_id).get('data')
        event = ticket.get('event')
        iso_date = event.get('date_begin')
        formatted_time = get_date_formatted_day_hour(iso_date)
        location = event.get('location')
        location_name = location.get('name')
        max_participants = event.get('max_participants')
        participants_count = event.get('participants_count')
        address = location.get('address')
        complete_address = f"{address.get('address1')}, {address.get('zip')}"
        keyboard = [[InlineKeyboardButton("Cancel", callback_data=f"cancelTicket_{ticket_id}")],
                    [InlineKeyboardButton("Back", callback_data="get_my_bookings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"Participants: {participants_count}/{max_participants}\nPlace: {location_name}\nAddress:{complete_address}\nDate: {formatted_time}",
            reply_markup=reply_markup)

    elif query.data.startswith("eventInfo_"):
        event_id = query.data.split("_")[1]
        event = event_info(event_id).get('data')
        iso_date = event.get('date_begin')
        formatted_time = get_date_formatted_day_hour(iso_date)
        location = event.get('location')
        location_name = location.get('name')
        max_participants = event.get('max_participants')
        participants_count = event.get('participants_count')
        address = location.get('address')
        complete_address = f"{address.get('address1')}, {address.get('zip')}"
        keyboard = [[InlineKeyboardButton("Register once", callback_data=f"registerEventOnce_{event_id}")],
                    [InlineKeyboardButton("Register series", callback_data=f"registerEventSeries_{event_id}")],
                    [InlineKeyboardButton("Back", callback_data=f"{get_weekday_form_date(iso_date)}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"Participants: {participants_count}/{max_participants}\nPlace: {location_name}\nAddress:{complete_address}\nDate: {formatted_time}",
            reply_markup=reply_markup)

    elif query.data.startswith("registerEventOnce_"):
        event_id = query.data.split("_")[1]
        register_data = register_event(event_id, telegram_user_id).get('data')
        current_status = register_data.get('current_status').get('status_name')
        if current_status == 'booked':
            await query.message.reply_text("Session booked successfully", callback_data='main_menu')
        else:
            await query.message.reply_text("Something went wrong. Please try again later.", callback_data='main_menu')

    elif query.data.startswith("registerEventSeries_"):
        event_id = query.data.split("_")[1]
        save_subscription(telegram_user_id, event_id)
        event = register_series(event_id, telegram_user_id)
        if event:
            await query.message.reply_text("Series booked successfully", callback_data='main_menu')
        else:
            await query.message.reply_text("Something went wrong. Please try again later.", callback_data='main_menu')


    elif query.data.startswith("changeCity_"):
        city = City[query.data.split("_")[1]]
        user_data[telegram_user_id]['current_city'] = city
        await query.message.reply_text(f"changed city to {city.value}")
        await query.message.reply_text("Main menu", reply_markup=main_menu_keyboard(telegram_user_id))

    elif query.data == "changeCity":
        buttons = [
            [InlineKeyboardButton(text=city.value, callback_data=f"changeCity_{city.name}")]
            for city in City
        ]

        await query.message.reply_text("Select your city", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "show_week_classes":
        buttons = [
            [InlineKeyboardButton(text=day.value[0], callback_data=f"{day.name}")]
            for day in DaysOfWeek
        ]
        buttons.append([InlineKeyboardButton(text='Back', callback_data='main_menu')])
        await query.message.reply_text(f"Select a week day", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data in [day.name for day in DaysOfWeek]:
        day = DaysOfWeek[query.data]
        all_events = events(await get_user_city(telegram_user_id), day)
        all_events_data = all_events.get('data')
        keyboard = []
        keyboard_row = []
        counter = 1
        for event in all_events_data:
            location = event.get('location')
            location_name = location.get('name')
            iso_date = event.get('date_begin')
            formatted_time = get_date_formatted_hour(iso_date)
            keyboard_row.append(
                InlineKeyboardButton(f"{location_name} {formatted_time}",
                                     callback_data=f"eventInfo_{event.get('id')}"))
            if counter % 2 == 0:
                keyboard.append(keyboard_row)
                keyboard_row = []

            counter += 1
        if keyboard_row:
            keyboard.append(keyboard_row)
        keyboard.append([InlineKeyboardButton("Back", callback_data="show_week_classes")])
        await query.message.reply_text(f"{day.value[0]} classes, total: {all_events.get('total')}",
                                       reply_markup=InlineKeyboardMarkup(keyboard))


async def get_user_city(telegram_user_id):
    return user_data.get(telegram_user_id, {}).get('current_city') or City.munich


async def get_my_bookings(query, telegram_user_id):
    try:
        tickets_response = tickets(telegram_user_id)
    except UnauthorizedException:
        clear_token(telegram_user_id)
        await query.message.reply_text("Please login again.")
        await query.message.reply_text("Main menu", reply_markup=main_menu_keyboard(telegram_user_id))
        return
    keyboard = []
    for ticket in tickets_response.get('data', []):
        event = ticket.get('event')
        iso_date = event.get('date_begin')
        formatted_time = get_date_formatted_day_hour(iso_date)
        location = event.get('location')
        location_name = location.get('name')
        ticket_id = ticket.get('id')
        keyboard.append(
            [InlineKeyboardButton(f"{location_name} - {formatted_time}",
                                  callback_data=f"ticketInfo_{ticket_id}")])
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    await query.message.reply_text(f"Total bookings: {tickets_response.get('total')}",
                                   reply_markup=InlineKeyboardMarkup(keyboard))


# Message handler for email and password input
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = update.effective_user.id

    # Check if the user is in the middle of the login process
    if telegram_user_id in user_data:
        step = user_data[telegram_user_id].get("step")

        if step == "email":
            # Save the email so we can ask for the password next
            user_data[telegram_user_id]["email"] = update.message.text
            user_data[telegram_user_id]["step"] = "password"

            await update.message.reply_text("Got it! Now enter your password:")

        elif step == "password":
            # Save the password and call the login API
            user_data[telegram_user_id]["password"] = update.message.text
            email = user_data[telegram_user_id]["email"]
            password = user_data[telegram_user_id]["password"]

            # Call the login API
            login_success = login(telegram_user_id, email, password)

            if login_success:
                await update.message.reply_text("Login successful! 🎉")
                await update.message.reply_text("Main menu", reply_markup=main_menu_keyboard(telegram_user_id))
            else:
                await update.message.reply_text("Login failed. Please try again.")

            # Clear user data after login attempt
            del user_data[telegram_user_id]

    else:
        await update.message.reply_text("Please click on the Login button to start the process.")


def main_menu_keyboard(telegram_user_id):
    user = get_user_by_user_id(telegram_user_id)
    if user and user.get('token'):
        if telegram_user_id not in user_data:
            user_data[telegram_user_id] = {}
        if 'current_city' not in user_data[telegram_user_id]:
            user_data[telegram_user_id]['current_city'] = City.munich
        current_city = user_data[telegram_user_id]['current_city']
        keyboard = [[InlineKeyboardButton("Get my bookings", callback_data="get_my_bookings")],
                    [InlineKeyboardButton("Show week classes", callback_data="show_week_classes")],
                    [InlineKeyboardButton(f"Change city(current: {current_city.value})", callback_data="changeCity")]]
    else:
        keyboard = [[InlineKeyboardButton("Login", callback_data="login")]]
    return InlineKeyboardMarkup(keyboard)


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
