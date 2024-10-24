import logging.config
import os

import requests
import telebot
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

from telegram_llm_chatbot.api.handlers import admin, chats, llm, users, welcome, image
from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(message, cfg.strings.help)


def start_bot():
    logger.info(f"Bot `{str(bot.get_me().username)}` has started")
    
    chats.register_handlers(bot)
    llm.register_handlers(bot)
    # image.register_handlers(bot)
    # users.register_handlers(bot)
    # admin.register_handlers(bot)
    # welcome.register_handlers(bot)
    
    #bot.infinity_polling()
    bot.polling()
