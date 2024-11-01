import logging.config
import os

import telebot
from dotenv import find_dotenv, load_dotenv

from telegram_llm_chatbot.api.handlers import admin, chats, image_gen, llm, welcome

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


def start_bot():
    """Start the bot."""
    logger.info(f"Bot `{str(bot.get_me().username)}` has started")

    chats.register_handlers(bot)
    llm.register_handlers(bot)
    image_gen.register_handlers(bot)
    admin.register_handlers(bot)
    welcome.register_handlers(bot)

    bot.infinity_polling(timeout=90)
