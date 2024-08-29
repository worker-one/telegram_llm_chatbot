from telegram_llm_chatbot.api.bot import start_bot
from telegram_llm_chatbot.db.database import create_tables

if __name__ == "__main__":
    create_tables()
    start_bot()
