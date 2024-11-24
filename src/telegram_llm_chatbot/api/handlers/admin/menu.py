
import logging
import logging.config

from omegaconf import OmegaConf
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_llm_chatbot.db import crud

config = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_menu_markup(options) -> InlineKeyboardMarkup:
    print(options)
    menu_markup = InlineKeyboardMarkup(row_width=1)
    menu_markup.add(
        InlineKeyboardButton(options.list_subscription_plan, callback_data="_list_subscription_plan"),
        InlineKeyboardButton(options.configure_subscription_plan, callback_data="_configure_subscription_plan"),
        InlineKeyboardButton(options.remove_subscription_plan, callback_data="_remove_subscription_plan"),
        InlineKeyboardButton(options.configure_language_model, callback_data="_configure_language_model"),
        InlineKeyboardButton(options.configure_image_model, callback_data="_configure_image_model"),
        InlineKeyboardButton(options.export_data, callback_data="_export_data"),
        InlineKeyboardButton(options.about, callback_data="_about")
    )
    return menu_markup


# react to any text if not command
def register_handlers(bot):
    """Register handlers for the bot."""

    @bot.message_handler(commands=["admin"])
    def admin_menu_command(message):
        user_id = message.from_user.id
        user = crud.get_user(user_id)

        if user.role != "admin":
            # inform that the user does not have rights
            bot.send_message(user_id, strings.no_rights.format(username=user.name))
            return

        # Send the admin menu
        bot.send_message(
            user_id, strings.admin_menu.title,
            reply_markup=create_admin_menu_markup(strings.admin_menu)
        )
