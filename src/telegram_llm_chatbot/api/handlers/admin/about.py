import logging
import logging.config

from omegaconf import OmegaConf


from telegram_llm_chatbot.api.db.export import export_table_to_df
from telegram_llm_chatbot.db import crud

config = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    @bot.callback_query_handler(func=lambda call: call.data == "_about")
    def about_handler(call):
        user_id = call.from_user.id

        config_str = OmegaConf.to_yaml(config)

        # Send config
        bot.send_message(user_id, f"```yaml\n{config_str}\n```", parse_mode="Markdown")
