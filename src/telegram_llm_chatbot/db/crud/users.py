import datetime
import logging
import time
from typing import Optional

from sqlalchemy.orm import Session
from tomlkit import date

from telegram_llm_chatbot.db.database import get_session
from telegram_llm_chatbot.db.models import Chat, Message, User, Log

# Load logging configuration with OmegaConf
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user(user_id: int) -> User:
    """
    Retrieve a user by their ID.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        User: The user object if found, otherwise None.
    """
    db: Session = get_session()
    result = db.query(User).filter(User.id == user_id).first()
    db.close()
    return result


def get_users() -> list[User]:
    """
    Retrieve all users.

    Returns:
        list[User]: A list of all user objects.
    """
    db: Session = get_session()
    result = db.query(User).all()
    db.close()
    return result


def get_chat(chat_id: int, user_id: int) -> Chat:
    """
    Retrieve a specific chat for a user.

    Args:
        chat_id (int): The ID of the chat to retrieve.
        user_id (int): The ID of the user who owns the chat.

    Returns:
        Chat: The chat object if found, otherwise None.
    """
    db: Session = get_session()
    result = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    db.close()
    return result


def get_chat_history(chat_id: int) -> list[Message]:
    """
    Retrieve the message history for a specific chat.

    Args:
        chat_id (int): The ID of the chat whose history to retrieve.

    Returns:
        list[Message]: A list of message objects associated with the chat.
    """
    db: Session = get_session()
    result = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp.asc()).all()
    db.close()
    return result


def upsert_user(user_id: int, name: str, last_chat_id: Optional[int] = None) -> User:
    """
    Insert or update a user.

    Args:
        user_id (int): The ID of the user.
        name (str): The name of the user.
        last_chat_id (Optional[int]): The ID of the last chat the user participated in.
    """
    db: Session = get_session()
    db.expire_on_commit = False
    try:
        user = db.query(User).filter(User.name == name, User.id == user_id).first()
        if user:
            user.name = name
            user.id = user_id
            if last_chat_id:
                user.current_chat_id = last_chat_id
        else:
            user = User(id=user_id, name=name)
            db.add(user)
        logger.info(f"User with name {user.name} added successfully.")
        db.commit()
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding user with name {name}: {e}")
    finally:
        db.close()


def delete_user(user_id: int) -> None:
    """
    Delete a user and all associated data.

    Args:
        user_id (int): The ID of the user to delete.
    """
    db: Session = get_session()
    try:
        # First, find the user's chats and associated messages
        user_chats = db.query(Chat).filter(Chat.user_id == user_id).all()

        for chat in user_chats:
            # Delete messages associated with each chat
            db_messages = db.query(Message).filter(Message.chat_id == chat.id).all()
            for message in db_messages:
                db.delete(message)

            # Delete the chat itself
            db.delete(chat)

        # Finally, delete the user
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)

        db.commit()
        logger.info(f"User with id {user_id} and all associated data deleted successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user with id {user_id}: {e}")
    finally:
        db.close()

def write_log(user_id: int, content: str) -> None:
    """
    Write a log entry for a user.

    Args:
        user_id (int): The ID of the user.
        content (str): The content of the log entry.
    """
    db: Session = get_session()
    try:
        db.add(Log(user_id=user_id, content=content, timestamp=datetime.datetime.now()))
        db.commit()
        logger.info(f"Log entry added for user with id {user_id}.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding log entry for user with id {user_id}: {e}")
    finally:
        db.close()
