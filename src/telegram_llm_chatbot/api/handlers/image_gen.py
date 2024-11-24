import logging.config

import requests
from hydra.utils import instantiate
from omegaconf import OmegaConf
from telebot import TeleBot
from telebot.states import State, StatesGroup
from telebot.states.sync.context import StateContext
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from telegram_llm_chatbot.core.image_gen import Dalle3OpenAI
from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")
config = OmegaConf.load("./src/telegram_llm_chatbot/conf/image_gen.yaml")

image_model_config = instantiate(config.dalle3)
dalle3 = Dalle3OpenAI(image_model_config)

class ImageGenStates(StatesGroup):
    awaiting_description = State()
    awaiting_size = State()

def register_handlers(bot: TeleBot):

    @bot.callback_query_handler(func=lambda call: call.data == "_cancel")
    def cancel_callback(call: CallbackQuery, state: StateContext):
        bot.send_message(call.message.chat.id, config.strings.cancelled)
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        state.delete()

    @bot.message_handler(commands=["generate"])
    def invoke_chatbot(message: Message, state: StateContext):
        user_id = int(message.chat.id)

        # Check active subscriptions
        crud.update_subscription_statuses(user_id)
        subscriptions = crud.get_active_subscriptions_by_user_id(user_id)
        if not subscriptions:
            purcharse_button = InlineKeyboardMarkup(row_width=1)
            purcharse_button.add(
                InlineKeyboardButton(strings.purcharse_subscription, callback_data="_purchase"),
            )
            bot.send_message(user_id, strings.account.no_subscription, reply_markup=purcharse_button)
            return

        cancel_button = InlineKeyboardMarkup(row_width=1)
        cancel_button.add(
            InlineKeyboardButton(config.strings.cancel, callback_data="_cancel"),
        )
        sent_message = bot.reply_to(message, config.strings.ask_description, reply_markup=cancel_button)
        state.set(ImageGenStates.awaiting_description)
        bot.register_next_step_handler(sent_message, handle_description, state)


    @bot.message_handler(state=ImageGenStates.awaiting_description)
    def handle_description(message: Message, state: StateContext):
        image_description = message.text
        user_id = message.chat.id

        # Create a menu to select the size
        size_menu = InlineKeyboardMarkup(row_width=3)
        for option in config.strings.ask_size.options:
            size_menu.add(
                InlineKeyboardButton(option["label"], callback_data=option['value']),
            )

        bot.send_message(
            user_id, config.strings.ask_size.title,
            reply_markup=size_menu
        )

        state.set(ImageGenStates.awaiting_size)
        state.add_data(image_description=image_description)

    @bot.callback_query_handler(state=ImageGenStates.awaiting_size)
    def handle_size(call: CallbackQuery, state: StateContext):
        image_size = call.data.replace("_", "")
        user_id = call.message.chat.id
        with state.data() as state_data:
            image_description = state_data["image_description"]

        try:
            bot.reply_to(call.message, config.strings.please_wait)
            response_content = dalle3.invoke(
                prompt=image_description, image_size=image_size
            )
            image_response = requests.get(response_content, timeout=60)
            if image_response.status_code == 200:
                bot.send_chat_action(chat_id=user_id, action="upload_photo")
                bot.send_photo(chat_id=user_id, photo=image_response.content)
            else:
                bot.reply_to(call.message, "Error downloading the image.")
        except Exception as e:
            logger.error(e)
            bot.reply_to(call.message, response_content)
        state.delete()

