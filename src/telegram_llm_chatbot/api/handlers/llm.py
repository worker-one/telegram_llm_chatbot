import logging.config

import requests
from omegaconf import OmegaConf

from telegram_llm_chatbot.db import database
from telegram_llm_chatbot.db import crud

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(
    OmegaConf.load("./src/telegram_llm_chatbot/conf/logging_config.yaml"),
    resolve=True
)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
base_url = cfg.service.base_url


def register_handlers(bot):
    # Define the command for invoking the chatbot
    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)
        user_message = message.text

        # add user to database if not already present
        if crud.get_user(user_id) is None:
            crud.upsert_user(user_id, message.chat.username)

            # add user via api
            response = requests.post(
                f"{base_url}/add_user",
                json={
                    "user": {
                        "id": user_id,
                        "name": message.chat.username
                    }
                }
            )

        last_chat_id = crud.get_last_chat_id(user_id)

        if last_chat_id is None:
            bot.reply_to(message, cfg.strings.no_chats)
            return

        response = requests.post(
            f"{base_url}/query",
            json={
                "user_id": user_id,
                "chat_id": last_chat_id,
                "user_message": user_message
            }
        )
        logger.info(response.json()['ai_message'])
        bot.reply_to(message, {response.json()['ai_message']}, parse_mode="markdown")
