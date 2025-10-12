import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Load environment variables from the .env file
load_dotenv()


class TelegramBot:
    def __init__(self):
        # Get Telegram bot token
        self.token = os.getenv("TG_TOKEN")
        if not self.token:
            raise ValueError("Telegram bot token is missing from the .env file as 'TG_TOKEN'.")

        # Create the application instance
        self.app = Application.builder().token(self.token).build()

        # Add a message handler
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles incoming text messages and prints them to the console.
        """
        user_message = update.message.text
        user_name = update.effective_user.first_name or "User"
        print(f"Message from {user_name}: {user_message}")

        # Optional: Reply to the user (uncomment if needed)
        await update.message.reply_text(f"Received your message: {user_message}")

    def run(self):
        """
        Start the bot and run it until the program is interrupted.
        """
        print("Bot is running... Press Ctrl+C to stop.")
        self.app.run_polling()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
