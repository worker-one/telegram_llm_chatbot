import logging.config
import os

import requests
from omegaconf import OmegaConf
from hydra.utils import instantiate

from telegram_llm_chatbot.core.text2image import Dalle3OpenAI
from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_text2image = OmegaConf.load("./src/telegram_llm_chatbot/conf/text2image.yaml")
image_model_config = instantiate(config_text2image.dalle3)
dalle3 = Dalle3OpenAI(image_model_config)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")

def download_file(bot, file_id, file_path):
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "wb") as file:
        file.write(downloaded_file)
    return file_path

def register_handlers(bot):
    @bot.message_handler(commands=["generate"])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)

        # add user to database if not already present
        if crud.get_user(user_id) is None:
            logger.info("New user {message.chat.username} added to database.")
            crud.upsert_user(user_id, message.chat.username)

        bot.reply_to(message, "Please provide a description for the image:")

        def handle_description(message):
            user_message = message.text
            user_id = message.chat.id
            logger.info(msg="User event", extra={"user_id": user_id, "user_message": user_message})
            try:
                response_content = dalle3.generate_image(prompt=user_message)
                image_response = requests.get(response_content)
                if image_response.status_code == 200:
                    bot.send_chat_action(chat_id=user_id, action="upload_photo")
                    bot.send_photo(chat_id=user_id, photo=image_response.content)
                else:
                    bot.reply_to(message, "Error downloading the image.")
            except Exception as e:
                bot.reply_to(message, f"Error generating image: {str(e)}")

        bot.register_next_step_handler(message, handle_description)

