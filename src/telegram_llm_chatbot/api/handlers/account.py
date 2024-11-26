import logging

from omegaconf import OmegaConf

from telegram_llm_chatbot.db import crud

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# load config from strings.yaml
strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")


def register_handlers(bot):

    @bot.message_handler(commands=["account"])
    def account(message):
        user_id = message.from_user.id
        username = message.from_user.username
        crud.update_subscription_statuses(user_id)
        subscriptions = crud.get_subscriptions_by_user_id(user_id)
        print(type(subscriptions), subscriptions)
        if subscriptions:
            for subscription in subscriptions:
                plan = crud.get_subscription_plan(subscription.plan_id)
                bot.send_message(
                    message.chat.id,
                    strings.account.subscription.format(
                        username=username,
                        plan=plan.name,
                        status=subscription.status,
                        start_date=subscription.start_date.strftime("%Y-%m-%d"),
                        end_date=subscription.end_date.strftime("%Y-%m-%d")
                    )
                )
        else:
            bot.send_message(message.chat.id, strings.account.no_subscription)
