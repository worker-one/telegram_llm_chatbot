import datetime
import logging
import logging.config
import os

import yaml
from omegaconf import OmegaConf
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_llm_chatbot.api.db.export import export_table_to_df
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



def create_period_selection_markup(strings):
    """Create the period selection markup."""
    period_markup = InlineKeyboardMarkup(row_width=1)
    period_markup.add(
        InlineKeyboardButton(strings.admin_menu.period_today, callback_data="_period_today"),
        InlineKeyboardButton(strings.admin_menu.period_week, callback_data="_period_week"),
        InlineKeyboardButton(strings.admin_menu.period_two_weeks, callback_data="_period_two_weeks"),
        InlineKeyboardButton(strings.admin_menu.period_month, callback_data="_period_month"),
        InlineKeyboardButton(strings.admin_menu.period_all, callback_data="_period_all"),
    )
    return period_markup


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

    @bot.callback_query_handler(func=lambda call: call.data == "_export_data")
    def export_data_handler(call):
        user_id = call.from_user.id

        # Send period selection menu
        bot.send_message(
            user_id, strings.admin_menu.select_period, reply_markup=create_period_selection_markup(strings)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("_period_"))
    def period_selection_handler(call):
        user_id = call.from_user.id

        period = call.data.split("_period_")[1]
        start_date = None

        if period == "today":
            start_date = datetime.datetime.now().date()
        elif period == "week":
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=7)
        elif period == "month":
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=30)
        elif period == "two_weeks":
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=14)
        else:
            start_date = None

        # Export data
        tables = ["chats", "messages", "users", "subscriptions", "subscription_plans"]
        for table in tables:
            df = export_table_to_df(table, start_date=start_date)

            # create a temp folder if it does not exist
            if not os.path.exists("temp"):
                os.makedirs("temp")

            # save as excel in temp folder and send to a user
            filename = f"temp/{table}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            bot.send_document(user_id, open(filename, "rb"))
            # remove the file
            os.remove(filename)

    @bot.callback_query_handler(func=lambda call: call.data == "_export_data")
    def export_data_handler(call):
        user_id = call.from_user.id

        # Send period selection menu
        bot.send_message(
            user_id, strings.admin_menu.select_period, reply_markup=create_period_selection_markup(strings)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("_period_"))
    def period_selection_handler(call):
        user_id = call.from_user.id

        period = call.data.split("_period_")[1]
        start_date = None

        if period == "today":
            start_date = datetime.datetime.now().date()
        elif period == "week":
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=7)
        elif period == "month":
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=30)
        elif period == "two_weeks":
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=14)
        else:
            start_date = None

        # Export data
        tables = ["chats", "messages", "users"]
        for table in tables:
            df = export_table_to_df(table, start_date=start_date)

            # create a temp folder if it does not exist
            if not os.path.exists("temp"):
                os.makedirs("temp")

            # save as excel in temp folder and send to a user
            filename = f"temp/{table}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            bot.send_document(user_id, open(filename, "rb"))
            # remove the file
            os.remove(filename)
