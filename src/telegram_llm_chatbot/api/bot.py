import logging.config
import os

import telebot
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf
from telebot import custom_filters
from telebot.states.sync.middleware import StateMiddleware

from telegram_llm_chatbot.api.handlers import account, admin, chats, image_gen, llm, subscription, welcome
from telegram_llm_chatbot.api.middlewares.antiflood import AntifloodMiddleware
from telegram_llm_chatbot.api.middlewares.user import UserCallbackMiddleware, UserMessageMiddleware

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

    # Handlers
    chats.register_handlers(bot)
    llm.register_handlers(bot)
    image_gen.register_handlers(bot)
    admin.register_handlers(bot)
    subscription.register_handlers(bot)
    account.register_handlers(bot)
    welcome.register_handlers(bot)

    # Middleware
    bot.setup_middleware(AntifloodMiddleware(bot, 2))
    bot.setup_middleware(UserMessageMiddleware())
    bot.setup_middleware(UserCallbackMiddleware())
    bot.setup_middleware(StateMiddleware(bot))

    # Add custom filters
    bot.add_custom_filter(custom_filters.StateFilter(bot))

    logger.info(f"Bot `{str(bot.get_me().username)}` has started")
    bot.infinity_polling(timeout=190)
    #bot.polling(timeout=90)
