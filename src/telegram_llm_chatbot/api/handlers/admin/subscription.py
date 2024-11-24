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


# react to any text if not command
def register_handlers(bot):
    """Register handlers for the bot."""

    @bot.callback_query_handler(func=lambda call: call.data == "_configure_subscription_plan")
    def configure_subscription_plan(call):
        user_id = call.from_user.id
        user = crud.get_user(user_id)
        if user.role != "admin":
            # Inform that the user does not have admin rights
            bot.send_message(user.id, strings.no_rights)
            return

        # Ask user to provide the subscription plan details
        sent_message = bot.send_message(user.id, strings.configure_subscription_ask)

        # Move to the next step: receiving the subscription plan details
        bot.register_next_step_handler(sent_message, get_subscription_plan, bot, user.id)

    # Handler to capture the subscription plan details from the user
    def get_subscription_plan(message, bot, user_id):
        user_input = message.text.split("\n")

        try:
            # Update database
            plan = crud.create_subscription_plan(
                name = user_input[0],
                description = user_input[1],
                price = float(user_input[2]),
                currency = user_input[3],
                duration_in_days = int(user_input[4])
            )
        except Exception as e:
            bot.send_message(user_id, "Format error. Please provide the details in the correct format.")
            return

        if plan:
            bot.send_message(
                user_id,
                strings.subscription_plan_created.format(
                    plan = f"Name: {plan.name}\nDescription: {plan.description}\nPrice: {plan.price} {plan.currency}\nDuration: {plan.duration_in_days} days"
                )
            )
        else:
            bot.send_message(user_id, strings.subscription_plan_not_created)

    @bot.callback_query_handler(func=lambda call: call.data == "_list_subscription_plan")
    def list_subscription_plan(call):
        user = crud.get_user(call.from_user.id)
        if user.role != "admin":
            # Inform that the user does not have admin rights
            bot.send_message(user.id, strings.no_rights)
            return

        plans = crud.get_subscription_plans()
        if plans:
            for plan in plans:
                bot.send_message(
                    user.id,
                    f"Name: {plan.name}, Price: {plan.price} {plan.currency}, Duration: {plan.duration_in_days} days"
                )
        else:
            bot.send_message(user.id, strings.subscription_plan_not_found)

    @bot.callback_query_handler(func=lambda call: call.data == "_remove_subscription_plan")
    def remove_subscription_plan(call):
        user = crud.get_user(call.from_user.id)
        if user.role != "admin":
            # Inform that the user does not have admin rights
            bot.send_message(user.id, strings.no_rights)
            return

        # Ask user to provide the subscription plan id
        sent_message = bot.send_message(user.id, strings.remove_subscription_ask)

        # Move to the next step: receiving the subscription plan id
        bot.register_next_step_handler(sent_message, remove_subscription_plan, bot, user.id)

    # Handler to remove the subscription plan
    def remove_subscription_plan(message, bot, user_id):
        plan_name = message.text
        plans = crud.get_subscription_plans(plan_name)
        if plans:
            for plan in plans:
                crud.delete_subscription_plan(plan.id)
            bot.send_message(user_id, strings.subscription_plan_removed.format(plan=plan_name))
        else:
            bot.send_message(user_id, strings.subscription_plan_not_found)
