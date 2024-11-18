import logging.config

from omegaconf import OmegaConf

from telegram_llm_chatbot.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = OmegaConf.load("./src/telegram_llm_chatbot/conf/welcome.yaml")


def register_handlers(bot):
    @bot.message_handler(commands=["help"])
    def help_command(message):
        """Handle the /help command."""
        user_id = int(message.chat.id)
        # add user to database if not already present
        if crud.get_user(user_id) is None:
            logger.info("New user {message.chat.username} added to database.")
            crud.upsert_user(user_id, message.chat.username)
        bot.reply_to(message, config.strings.help)

    @bot.message_handler(commands=["start"])
    def start_command(message):
        """Handle the /start command."""
        user_id = int(message.chat.id)
        # add user to database if not already present
        if crud.get_user(user_id) is None:
            logger.info("New user {message.chat.username} added to database.")
            crud.upsert_user(user_id, message.chat.username)
        bot.reply_to(message, config.strings.start)