import logging.config
import os

import requests
import telebot
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

from telegram_llm_chatbot.api.handlers import chats

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("./src/telegram_llm_chatbot/conf/logging_config.yaml"), resolve=True)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
chats.register_handlers(bot)
cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")

# Define the base URL of your API
base_url = cfg.service.base_url

@bot.message_handler(commands=["help"])
def help_command(message):
    user_id = message.from_user.id
    bot.reply_to(message, cfg.strings.help)

# Define the command for invoking the chatbot
@bot.message_handler(commands=['invoke'])
def invoke_chatbot(message):
    user_id, chat_id, user_message = message.text.split()[1:]
    response = requests.post(f"{base_url}/invoke", json={"user_id": user_id, "chat_id": chat_id, "user_message": user_message})
    bot.reply_to(message, f"AI responded with message: {response.json()['ai_message']}")

# Define the command for adding users
@bot.message_handler(commands=['add_users'])
def add_users(message):
    users_data = message.text.split()[1:]
    users_list = [{"id": user_data[0], "name": user_data[1]} for user_data in users_data]
    response = requests.post(f"{base_url}/add_users", json={"users": users_list})
    bot.reply_to(message, response.json()["message"])

# Define the command for getting users
@bot.message_handler(commands=['get_users'])
def get_users(message):
    response = requests.get(f"{base_url}/get_users")
    bot.reply_to(message, f"Users: {response.json()}")


def start_bot():
    logger.info(f"Bot `{str(bot.get_me().username)}` has started")
    bot.infinity_polling()
