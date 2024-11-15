import logging
import os

from telegram_llm_chatbot.db import crud
from telegram_llm_chatbot.db.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(bot, file_id: str, file_path: str) -> None:
    """
    Downloads a file from Telegram servers and saves it to the specified path.

    Args:
        bot: The Telegram bot instance.
        file_id: The unique identifier for the file to be downloaded.
        file_path: The local path where the downloaded file will be saved.
    """
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "wb") as file:
        file.write(downloaded_file)
    logger.info(msg="OS event", extra={"file_id": file_id, "file_path": file_path, "event": "download_file"})


def user_sign_in(user_id: int, message) -> User:
    """
    Signs in a user by adding them to the database if they are not already present.

    Args:
        user_id: The unique identifier for the user.
        message: The message object containing user information.

    Returns:
        User: The user object.
    """
    logger.info("User event", extra={"user_id": user_id, "user_message": message.text})
    user = crud.get_user(user_id)
    if user is None:
        logger.info(f"DB user {message.chat.username} added to database.")
        user = crud.upsert_user(user_id, message.chat.username)

        # Add trial subscription to user
        crud.create_subscription(user_id, 1, "active")

    return user


def is_command(message):
    """
    Checks if the message is a command (starts with '/').
    """
    return bool(message.text and message.text.startswith("/"))


def parse_callback_data(data):
    """Parse callback data to extract chat ID and name."""
    parts = data.split("_")
    return int(parts[2]), parts[3]
