import logging
import logging.config

import yaml
from omegaconf import OmegaConf

config = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# react to any text if not command
def register_handlers(bot):
    """Register handlers for the bot."""
    @bot.callback_query_handler(func=lambda call: call.data == "_configure_language_model")
    def configure_language_model_handler(call):
        user_id = call.from_user.id

        # Ask for new configuration values
        msg = bot.send_message(user_id, strings.admin_menu.enter_new_config)
        bot.register_next_step_handler(msg, process_new_config)

    def process_new_config(message):
        user_id = message.from_user.id
        new_config = message.text

        try:
            # Parse the new configuration values
            new_config_dict = yaml.safe_load(new_config)

            # Load the existing llm.yaml file
            with open("./src/telegram_llm_chatbot/conf/llm.yaml", "r") as file:
                llm_config = yaml.safe_load(file)

            # Update the custom key with new values
            llm_config["custom"].update(new_config_dict)

            # Save the updated configuration back to the file
            with open("./src/telegram_llm_chatbot/conf/llm.yaml", "w") as file:
                yaml.safe_dump(llm_config, file)

            bot.send_message(user_id, strings.admin_menu.config_update_success)
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            bot.send_message(user_id, strings.admin_menu.config_update_failed)