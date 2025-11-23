"""Main entry point for Phoenix Bot."""
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.core import Container
from src.core.config import settings


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


async def main():
    """Main function to run the bot."""
    # Setup logging
    setup_logging()
    
    # Create DI container
    container = Container()
    
    # Get the telegram handler from container
    telegram_handler = container.telegram_handler()
    
    # Create the Application and pass it the bot's token
    application = Application.builder().token(settings.telegram_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", telegram_handler.start_command))
    application.add_handler(CommandHandler("command", telegram_handler.command_list))
    application.add_handler(CommandHandler("commands", telegram_handler.command_list))
    application.add_handler(CommandHandler("help", telegram_handler.command_list))
    application.add_handler(CommandHandler("profile", telegram_handler.profile_command))
    application.add_handler(CommandHandler("balance", telegram_handler.balance_command))
    application.add_handler(CommandHandler("top", telegram_handler.top_command))
    application.add_handler(CommandHandler("daily", telegram_handler.daily_command))
    application.add_handler(CommandHandler("adm", telegram_handler.admin_command))
    application.add_handler(CommandHandler("admin", telegram_handler.admin_command))
    
    # Additional game command handlers would go here
    # These are placeholders for now:
    # application.add_handler(CommandHandler("blackjack", game_handler.blackjack_command))
    # application.add_handler(CommandHandler("dice", game_handler.dice_command))
    # application.add_handler(CommandHandler("rps", game_handler.rps_command))
    # application.add_handler(CommandHandler("duel", game_handler.duel_command))
    # application.add_handler(CommandHandler("clan", clan_handler.clan_command))
    
    # Run the bot until the user presses Ctrl-C
    await application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())