import logging.config

import requests
from omegaconf import OmegaConf

from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
base_url = cfg.service.base_url


def register_handlers(bot):
    # Define the command for invoking the chatbot
    @bot.message_handler(func=lambda message: message.text[0] != '/', content_types=['text'])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)
        user_message = message.text

        # add user to database if not already present
        if crud.get_user(user_id) is None:
            crud.upsert_user(user_id, message.chat.username)

        response = requests.get(f"{base_url}/users/{user_id}")
        if response.status_code == 404:
            # add user via api
            response = requests.post(
                f"{base_url}/users",
                json={
                    "user": {
                        "id": user_id,
                        "name": message.chat.username
                    }
                }
            )
            if response.status_code == 200:
                logger.info(f"User with id {user_id} added successfully.")
            else:
                logger.error(f"Error adding user with id {user_id}: {response.json()['message']}")

        last_chat_id = crud.get_last_chat_id(user_id)

        if last_chat_id is None:
            bot.reply_to(message, cfg.strings.no_chats)
            return

        response = requests.post(
            f"{base_url}/model/query",
            json={
                "user_id": user_id,
                "chat_id": last_chat_id,
                "user_message": user_message
            }
        )
        ai_message = response.json()['model_response']['response_content']
        bot.send_chat_action(chat_id=user_id, action="typing")
        bot.send_message(message.chat.id, ai_message, parse_mode="markdown")
