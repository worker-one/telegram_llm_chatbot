import logging.config

import requests
from omegaconf import OmegaConf
from telebot import types

from telegram_llm_chatbot.db import crud, database

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("./src/telegram_llm_chatbot/conf/logging_config.yaml"), resolve=True)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

cfg = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
base_url = cfg.service.base_url


def register_handlers(bot):
    # Define the command for adding a chat
    @bot.message_handler(commands=['add_chat'])
    def add_chat(message):
        user_id = int(message.chat.id)

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
        logger.info(response.json()["message"])

        # add chat for the user
        chat_name = message.text.split(' ')[1]
        response = requests.post(
            f"{base_url}/add_chat",
            json={
                "user_id": user_id,
                "chat_name": chat_name
            }
        )
        bot.reply_to(message, response.json()["message"])

    @bot.message_handler(commands=['current_chat'])
    def current_chat(message):
        user_id = int(message.chat.id)
        db = database.get_session()
        chat_id = crud.get_last_chat_id(db, user_id)
        if chat_id:
            bot.reply_to(message, f"Your current chat is {chat_id}")
        else:
            bot.reply_to(message, "You have not selected any chat yet. Use /get_chats to select a chat.")

    # Define the command for getting chats
    @bot.message_handler(commands=['get_chats'])
    def get_chats(message):
        user_id = int(message.chat.id)
        response = requests.post(
            f"{base_url}/get_chats",
            json={"user_id": user_id},
            timeout=10
        )
        chats = response.json()['chats']

        markup = types.InlineKeyboardMarkup()
        for chat in chats:
            button = types.InlineKeyboardButton(
                text=chat['chat_name'],
                callback_data=f"chat_{chat['chat_id']}"
            )
            markup.add(button)

        if chats:
            bot.send_message(chat_id=message.chat.id, text="Here are your chats:", reply_markup=markup)
        else:
            bot.send_message(chat_id=message.chat.id, text="You have no chats.")
    @bot.callback_query_handler(func=lambda call: "chat_" in call.data)
    def handle_callback_query(call):
        chat_id = int(call.data.split('_')[1])
        user_id = call.from_user.id

        # Get a new session
        db = database.get_session()

        # Update the last_chat_id for the user
        crud.update_user(db, user_id, call.from_user.username, last_chat_id=chat_id)

        logger.info(f"User with id {user_id} updated successfully with chat_id {chat_id}.")
        # Send a message to the user
        bot.send_message(chat_id=call.message.chat.id, text=f"You have selected chat {chat_id}")

    # Define the command for deleting a chat
    @bot.message_handler(commands=['delete_chat'])
    def delete_chat(message):
        user_id = int(message.chat.id)
        chat_id = int(message.text.split(' ')[1])
        response = requests.post(
            f"{base_url}/delete_chat",
            json={
                "user_id": user_id,
                "chat_id": chat_id
            }
        )
        bot.reply_to(message, response.json()["message"])
