from omegaconf import OmegaConf

strings = OmegaConf.load("./src/telegram_llm_chatbot/conf/strings.yaml")


def register_handlers(bot):
    @bot.message_handler(commands=["help"])
    def help_handler(message):
        bot.reply_to(message, strings.help)
