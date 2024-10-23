import os
import logging.config

import requests
from omegaconf import OmegaConf

from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
base_url = os.getenv("LLM_API")

def download_file(bot, file_id, file_path):
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "wb") as file:
        file.write(downloaded_file)
    return file_path


def is_command(message):
    if message.text is None:
        return False
    elif message.text.startswith("/"):
        return True
    else:
        return False


def register_handlers(bot):
    # Define the command for invoking the chatbot
    @bot.message_handler(func=lambda message: not is_command(message), content_types=['text', 'photo', 'document'])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)

        # add user to database if not already present
        if crud.get_user(user_id) is None:
            crud.upsert_user(user_id, message.chat.username)

        response = requests.get(f"{base_url}/users/users/{user_id}")
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

        if message.content_type in ["photo", "document"]:
            user_message = message.caption if message.caption else ""
            file_id = message.photo[-1].file_id if message.content_type == "photo" else message.document.file_id
            filename = message.photo[-1].file_name if message.content_type == "photo" else message.document.file_name
            user_input_image_path = f"./.tmp/files/{user_id}/{filename}"
            logger.info(msg="User event", extra={"user_id": user_id, "user_message": user_message})
            try:
                download_file(bot, file_id, user_input_image_path)
                files = {"files": open(user_input_image_path, "rb")}
                data = {"user_id": user_id, "chat_id": last_chat_id, "user_message": user_message}
                response = requests.post(f"{base_url}/llm/query", files=files, data=data)
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
                bot.reply_to(message, f"Error downloading image: {e}")
                return
        else:
            user_message = message.text
            logger.info(msg="User event", extra={"user_id": user_id, "user_message": user_message})
            data = {"user_id": user_id, "chat_id": last_chat_id, "user_message": user_message}
            response = requests.post(f"{base_url}/llm/query", data=data)

        response_content = response.json()['model_response']['response_content']
        bot.send_chat_action(chat_id=user_id, action="typing")
        bot.send_message(message.chat.id, response_content, parse_mode="markdown")
