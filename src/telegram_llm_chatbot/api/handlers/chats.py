import logging.config

from omegaconf import OmegaConf
from telebot import types

from telegram_llm_chatbot.api.common import parse_callback_data, user_sign_in
from telegram_llm_chatbot.db import crud

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load strings configuration
strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")


def register_handlers(bot):
    """Register handlers for the bot."""

    @bot.message_handler(commands=["add_chat"])
    def add_chat(message):
        """Handle the /add_chat command."""
        user_id = int(message.chat.id)
        user_sign_in(user_id, message)
        bot.reply_to(message, strings.add_chat_ask_name)
        bot.register_next_step_handler(message, _add_chat)

    def _add_chat(message):
        """Handle the next step for adding a chat."""
        user_id = int(message.chat.id)
        chat_name = message.text

        try:
            new_chat = crud.create_chat(user_id, chat_name)
            crud.update_user_last_chat_id(user_id, new_chat.id)
            bot.reply_to(message, strings.add_chat_success.format(chat_name=chat_name))
            bot.reply_to(message, strings.current_chat.format(chat_name=chat_name))
        except Exception as e:
            logger.error(f"Error creating chat for user {user_id}: {e}")
            bot.reply_to(message, strings.add_chat_error)

    @bot.message_handler(commands=["current_chat"])
    def current_chat(message):
        """Handle the /current_chat command."""
        user_id = int(message.chat.id)
        user_sign_in(user_id, message)
        chat_id = crud.get_last_chat_id(user_id)

        if chat_id:
            try:
                chat_name = crud.get_chat_name(user_id, chat_id)
                bot.reply_to(message, strings.current_chat.format(chat_name=chat_name))
            except IndexError:
                bot.reply_to(message, strings.current_chat_no_chat)
        else:
            bot.reply_to(message, strings.current_chat_no_chat)

    @bot.message_handler(commands=["get_chats"])
    def get_chats(message):
        """Handle the /get_chats command."""
        user_id = int(message.chat.id)
        user_sign_in(user_id, message)
        chats = crud.get_user_chats(user_id)
        send_chats_list(bot, message.chat.id, chats, strings.get_chats, strings.get_chats_empty)

    @bot.callback_query_handler(func=lambda call: "select_chat_" in call.data)
    def select_chat_callback_query(call):
        """Handle the callback query for selecting a chat."""
        chat_id, chat_name = parse_callback_data(call.data)
        user_id = call.from_user.id

        try:
            crud.upsert_user(user_id, call.from_user.username, last_chat_id=chat_id)
            logger.info(f"User with id {user_id} updated successfully with chat_id {chat_id}.")
            bot.send_message(
                chat_id=call.message.chat.id, text=strings.handle_callback_query_success.format(chat_name=chat_name)
            )
        except Exception as e:
            logger.error(f"Error updating user with id {user_id}: {e}")
            bot.send_message(chat_id=call.message.chat.id, text="An error occurred. Please try again later.")

    @bot.message_handler(commands=["delete_chat"])
    def delete_chat(message):
        """Handle the /delete_chat command."""
        user_id = int(message.chat.id)
        user_sign_in(user_id, message)
        chats = crud.get_user_chats(user_id)

        if not chats:
            bot.send_message(chat_id=message.chat.id, text=strings.get_chats_empty)
        else:
            send_chats_list(
                bot, message.chat.id, chats, strings.delete_chat_ask, strings.get_chats_empty, "delete_chat_"
            )

    @bot.callback_query_handler(func=lambda call: "delete_chat_" in call.data)
    def delete_chat_callback_query(call):
        """Handle the callback query for deleting a chat."""
        user_id = int(call.from_user.id)
        chat_id, chat_name = parse_callback_data(call.data)

        try:
            crud.delete_chat(user_id, chat_id)
            bot.send_message(chat_id=user_id, text=strings.delete_chat_success.format(chat_name=chat_name))
            chats = crud.get_user_chats(user_id)
            send_chats_list(bot, call.message.chat.id, chats, strings.get_chats, strings.get_chats_empty)
        except Exception as e:
            logger.error(f"Error deleting chat with id {chat_id} for user {user_id}: {e}")
            bot.send_message(chat_id=user_id, text=strings.delete_chat_error)


def send_chats_list(bot, chat_id, chats, message_text, empty_message_text, callback_prefix="select_chat_"):
    """Send a list of chats to the user."""
    if chats:
        markup = types.InlineKeyboardMarkup()
        for chat in chats:
            button = types.InlineKeyboardButton(text=chat.name, callback_data=f"{callback_prefix}{chat.id}_{chat.name}")
            markup.add(button)
        bot.send_message(chat_id=chat_id, text=message_text, reply_markup=markup)
    else:
        bot.send_message(chat_id=chat_id, text=empty_message_text)
