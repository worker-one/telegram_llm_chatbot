import logging.config

import requests
from omegaconf import OmegaConf
from telebot import TeleBot


# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("./src/telegram_llm_chatbot/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
base_url = cfg.service.base_url


def register_handlers(bot: TeleBot):
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
