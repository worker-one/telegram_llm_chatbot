import logging.config
import os

import telebot
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

from telegram_llm_chatbot.api.handlers import admin, chats, image_gen, llm, welcome
from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")


@bot.message_handler(commands=["help"])
def help_command(message):
    """Handle the /help command."""
    user_id = int(message.chat.id)
    # add user to database if not already present
    if crud.get_user(user_id) is None:
        logger.info("New user {message.chat.username} added to database.")
        crud.upsert_user(user_id, message.chat.username)
    bot.reply_to(message, strings.strings.help)


def start_bot():
    """Start the bot."""
    logger.info(f"Bot `{str(bot.get_me().username)}` has started")

    chats.register_handlers(bot)
    llm.register_handlers(bot)
    image_gen.register_handlers(bot)
    admin.register_handlers(bot)
    welcome.register_handlers(bot)

    bot.infinity_polling()
    #bot.polling()
