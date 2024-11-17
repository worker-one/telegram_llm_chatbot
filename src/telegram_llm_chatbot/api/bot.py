import logging.config
import os

import telebot
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

from telegram_llm_chatbot.api.middlewares.antiflood import AntifloodMiddleware
from telegram_llm_chatbot.api.handlers import account, admin, chats, image_gen, llm, subscription, welcome

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

config = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")

bot = telebot.TeleBot(BOT_TOKEN, use_class_middlewares=True, parse_mode=None)


def start_bot():
    logger.info(f"{config.app.name} v{config.app.version}")
    logger.info(f"Bot `{str(bot.get_me().username)}` has started")

    # Handlers
    chats.register_handlers(bot)
    llm.register_handlers(bot)
    image_gen.register_handlers(bot)
    admin.register_handlers(bot)
    subscription.register_handlers(bot)
    account.register_handlers(bot)
    welcome.register_handlers(bot)
    welcome.register_handlers(bot)

    # Middleware
    bot.setup_middleware(AntifloodMiddleware(bot, 2))

    bot.infinity_polling(timeout=90)
    #bot.polling(timeout=90)
