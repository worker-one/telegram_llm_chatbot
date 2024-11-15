import datetime
import logging
import os

from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf
from telebot.types import LabeledPrice

from telegram_llm_chatbot.db import crud

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# load environment variables
load_dotenv(find_dotenv(usecwd=True))
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")

strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")


def register_handlers(bot):

    @bot.message_handler(commands=["purchase"])
    def purchase(message):
        subscription_plans = crud.get_subscription_plans()
        for subscription_plan in subscription_plans:
            if subscription_plan.price > 0:
                prices = [LabeledPrice(label=subscription_plan.name, amount=int(subscription_plan.price*100))]
                bot.send_invoice(
                    chat_id = message.chat.id,
                    title = subscription_plan.name,
                    description = subscription_plan.description or " ",
                    provider_token = PROVIDER_TOKEN,
                    currency = subscription_plan.currency,
                    prices = prices,
                    invoice_payload = subscription_plan.id,
                    is_flexible=False,
                    start_parameter='premium-example'
                )

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(pre_checkout_query):
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                    error_message="Try to pay again in a few minutes, we need a small rest.")

    @bot.message_handler(content_types=['successful_payment'])
    def successful_payment(message):
        user_id = message.from_user.id
        subscription_plan_id = message.successful_payment.invoice_payload
        subscription = crud.create_subscription(user_id, subscription_plan_id)
        crud.create_payment(
            subscription_id=subscription.id,
            amount=message.successful_payment.total_amount/100,
            currency=message.successful_payment.currency,
            payment_date=datetime.datetime.now(),
            payment_method=message.successful_payment.provider_payment_charge_id
        )
        bot.send_message(user_id, strings.payment_successful.format(product_name=subscription.plan.name))
        logger.info(f"User {user_id} has successfully paid for subscription {subscription_plan_id}")
