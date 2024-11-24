from telegram_llm_chatbot.api.handlers.admin import db, menu, subscription, about, config

def register_handlers(bot):
    db.register_handlers(bot)
    menu.register_handlers(bot)
    config.register_handlers(bot)
    about.register_handlers(bot)
    subscription.register_handlers(bot)