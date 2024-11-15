import logging.config

import requests
from hydra.utils import instantiate
from omegaconf import OmegaConf
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_llm_chatbot.api.common import user_sign_in
from telegram_llm_chatbot.core.image_gen import Dalle3OpenAI
from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_image_gen = OmegaConf.load("./src/telegram_llm_chatbot/conf/image_gen.yaml")
image_model_config = instantiate(config_image_gen.dalle3)
dalle3 = Dalle3OpenAI(image_model_config)

strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")


def register_handlers(bot):

    @bot.callback_query_handler(func=lambda call: call.data == "_cancel")
    def cancel_callback(call):
        bot.send_message(call.message.chat.id, "Operation cancelled.")
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

    @bot.message_handler(commands=["generate"])
    def invoke_chatbot(message):
        user_id = int(message.chat.id)
        user = user_sign_in(user_id, message)

        # Check active subscriptions
        subscriptions = crud.get_active_subscriptions_by_user_id(user_id)
        if not subscriptions:
            bot.send_message(user_id, "You need an active subscription to use this service. Use /purchase to buy one.")
            return

        cancel_button = InlineKeyboardMarkup(row_width=1)
        cancel_button.add(
            InlineKeyboardButton("Cancel", callback_data="_cancel"),
        )
        bot.reply_to(message, strings.image_gen.ask_description, reply_markup=cancel_button)

        def handle_description(message):
            user_message = message.text
            user_id = message.chat.id
            logger.info(msg="User event", extra={"user_id": user_id, "user_message": user_message})
            try:
                bot.reply_to(message, strings.image_gen.please_wait)
                response_content = dalle3.generate_image(prompt=user_message)
                image_response = requests.get(response_content, timeout=(160, 360))
                if image_response.status_code == 200:
                    bot.send_chat_action(chat_id=user_id, action="upload_photo")
                    bot.send_photo(chat_id=user_id, photo=image_response.content)
                else:
                    bot.reply_to(message, "Error downloading the image.")
            except Exception as e:
                bot.reply_to(message, response_content)

        bot.register_next_step_handler(message, handle_description)
