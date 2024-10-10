from omegaconf import OmegaConf

config = OmegaConf.load("./src/telegram_llm_chatbot/conf/config.yaml")
strings = config.strings

def register_handlers(bot):

    @bot.message_handler(commands=['help'])
    def help_handler(message):
        bot.reply_to(message, strings.help)
