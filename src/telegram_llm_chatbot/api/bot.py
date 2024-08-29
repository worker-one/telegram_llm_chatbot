import logging.config
import os

import telebot
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

from telegram_llm_chatbot.api.handlers import chats, llm, users
from telegram_llm_chatbot.db import crud, database

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("./src/telegram_llm_chatbot/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
chats.register_handlers(bot)
llm.register_handlers(bot)
users.register_handlers(bot)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")

# Define the base URL of your API
base_url = cfg.service.base_url

@bot.message_handler(commands=["help"])
def help_command(message):
    user_id = message.from_user.id

    # add user to database if not already present
    db = database.get_session()
    crud.add_user(db, user_id, message.from_user.username)

    bot.reply_to(message, cfg.strings.help)


def start_bot():
    logger.info(f"Bot `{str(bot.get_me().username)}` has started")
    bot.infinity_polling()
