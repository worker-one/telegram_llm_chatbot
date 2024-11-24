import logging

from telebot.handler_backends import BaseMiddleware
from telebot.types import CallbackQuery, Message

from telegram_llm_chatbot.db import crud

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class UserMessageMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.update_types = ['message']

    def pre_process(self, message: Message, data: dict):
        user = crud.upsert_user(
            user_id=message.from_user.id,
            name=message.from_user.username
        )
        crud.write_log(
            user_id=user.id,
            content=message.text
        )
        logger.info(f"User: '{message.from_user.username}', message: '{message.text}'")
        data['user'] = user

    def post_process(self, message, data, exception):
        pass


class UserCallbackMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.update_types = ['callback_query']

    def pre_process(self, callback_query: CallbackQuery, data: dict):
        user = crud.upsert_user(
            user_id=callback_query.from_user.id,
            name=callback_query.from_user.username
        )
        crud.write_log(
            user_id=user.id,
            content=callback_query.data
        )
        logger.info(f"User: '{callback_query.from_user.username}', callback_data: '{callback_query.data}'")
        data['user'] = user

    def post_process(self, callback_query, data, exception):
        pass