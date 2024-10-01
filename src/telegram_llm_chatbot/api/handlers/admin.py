import datetime
import logging
import logging.config
import os

from omegaconf import OmegaConf
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_llm_chatbot.api.db.export import export_table_to_df
from telegram_llm_chatbot.db.crud import get_user

config = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
strings = config.strings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_menu_markup(strings):
    menu_markup = InlineKeyboardMarkup(row_width=1)
    menu_markup.add(
        InlineKeyboardButton(strings.admin_menu.export_data, callback_data="_export_data"),
    )
    return menu_markup


# react to any text if not command
def register_handlers(bot):
    @bot.message_handler(commands=["admin"])
    def admin_menu_command(message):
        user_id = message.from_user.id
        user = get_user(user_id)

        if user.username.lower() not in ["sashagvozd", "konverner"]:
            # inform that the user does not have rights
            bot.send_message(user_id, strings.no_rights.format(username=user.username))
            return

        # Send the admin menu
        bot.send_message(
            user_id, strings.admin_menu.title,
            reply_markup=create_admin_menu_markup(strings)
        )

    @bot.callback_query_handler(func=lambda call: call.data == "_export_data")
    def query_handler(message):
        user_id = message.from_user.id
        user = get_user(user_id)

        if user.username not in ["gvozd_aa", "konverner"]:
            # inform that the user does not have rights
            bot.send_message(user_id, strings.no_rights)
            return

        # Export data
        tables = ['chats', 'messages', 'users']
        for table in tables:
            df = export_table_to_df(table)

            # create a temp folder if it does not exist
            if not os.path.exists('temp'):
                os.makedirs('temp')

            # save as excel in temp folder and send to a user
            filename = f"temp/{table}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            bot.send_document(user_id, open(filename, 'rb'))
            # remove the file
            os.remove(filename)
