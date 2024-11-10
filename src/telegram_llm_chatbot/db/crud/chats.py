import logging
from datetime import datetime

from sqlalchemy.orm import Session

from telegram_llm_chatbot.db.database import get_session
from telegram_llm_chatbot.db.models import Chat, Message, User

# Load logging configuration with OmegaConf
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_chat(user_id: int, name: str) -> Chat:
    """
    Create a new chat for a user.

    Args:
        user_id (int): The ID of the user who owns the chat.
        name (str): The name of the chat.

    Returns:
        Chat: The created chat object.
    """
    db: Session = get_session()
    db_chat = Chat(user_id=user_id, name=name)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    db.close()
    return db_chat


def get_user_chats(user_id: int) -> list[Chat]:
    """
    Retrieve all chats for a specific user.

    Args:
        user_id (int): The ID of the user whose chats to retrieve.

    Returns:
        list[Chat]: A list of chat objects associated with the user.
    """
    db: Session = get_session()
    result = db.query(Chat).filter(Chat.user_id == user_id).all()
    db.close()
    return result


def delete_chat(user_id: int, chat_id: int) -> None:
    """
    Delete a chat and all associated messages.

    Args:
        user_id (int): The ID of the user who owns the chat.
        chat_id (int): The ID of the chat to delete.
    """
    db: Session = get_session()
    # First, delete the messages associated with the chat
    db_messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    for message in db_messages:
        db.delete(message)

    # Then, delete the chat
    db_chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    db.delete(db_chat)
    db.commit()
    db.close()


def create_message(chat_id: int, role: str, content: str, timestamp: datetime) -> Message:
    """
    Create a new message in a chat.

    Args:
        chat_id (int): The ID of the chat to add the message to.
        role (str): The role of the message sender.
        content (str): The content of the message.
        timestamp (datetime): The timestamp of the message.

    Returns:
        Message: The created message object.
    """
    db: Session = get_session()
    db_message = Message(chat_id=chat_id, role=role, content=content, timestamp=timestamp)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    db.close()
    return db_message


def get_last_chat_id(user_id: int) -> int:
    """
    Retrieve the last chat ID for a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        int: The ID of the last chat the user participated in.
    """
    db: Session = get_session()
    result = db.query(User).filter(User.id == user_id).first()
    db.close()
    return result.current_chat_id


def get_chat_name(user_id: int, chat_id: int) -> str:
    """
    Retrieve the name of a chat.

    Args:
        user_id (int): The ID of the user who owns the chat.
        chat_id (int): The ID of the chat.

    Returns:
        str: The name of the chat.
    """
    db: Session = get_session()
    result = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    db.close()
    return result.name


def update_user_last_chat_id(user_id: int, chat_id: int) -> Chat:
    """
    Update the last chat ID for a user.

    Args:
        user_id (int): The ID of the user.
        chat_id (int): The ID of the chat to set as the last chat.

    Returns:
        Chat: The updated user object.
    """
    db: Session = get_session()
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.current_chat_id = chat_id
    db.commit()
    db.close()
    return db_user
