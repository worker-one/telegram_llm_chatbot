import logging
from datetime import datetime
from telegram_llm_chatbot.db.database import get_session
from telegram_llm_chatbot.db.models import Chat, Message, User
from sqlalchemy.orm import Session


# Load logging configuration with OmegaConf
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user(user_id: int) -> User:
    db: Session = get_session()
    result = db.query(User).filter(User.id == user_id).first()
    db.close()
    return result

def get_users() -> list[User]:
    db: Session = get_session()
    result = db.query(User).all()
    db.close()
    return result

def get_user_chats(user_id: int) -> list[Chat]:
    db: Session = get_session()
    result = db.query(Chat).filter(Chat.user_id == user_id).all()
    db.close()
    return result

def get_chat(chat_id: int, user_id: int) -> Chat:
    db: Session = get_session()
    result = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    db.close()
    return result

def get_chat_history(chat_id: int) -> list[Message]:
    db: Session = get_session()
    result = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.timestamp.asc()).all()
    db.close()
    return result


def upsert_user(user_id: int, name: str):
    db: Session = get_session()
    try:
        user = db.query(User).filter(User.name == name, User.id == user_id).first()
        if user:
            user.name = name
            user.id = user_id
            logger.info(f"User with id {name} updated successfully.")
        else:
            new_user = User(id = user_id, name=name)
            db.add(new_user)
            logger.info(f"User with name {name} added successfully.")
        db.commit()
    finally:
        db.close()

def delete_user(user_id: int) -> None:
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

def create_chat(user_id: int, name: str) -> Chat:
    db: Session = get_session()
    db_chat = Chat(user_id=user_id, name=name)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    db.close()
    return db_chat

def delete_chat(user_id: int, chat_id: int) -> None:
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
    db: Session = get_session()
    db_message = Message(chat_id=chat_id, role=role, content=content, timestamp=timestamp)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    db.close()
    return db_message

def get_last_chat_id(user_id: int) -> int:
    db: Session = get_session()
    result = db.query(User).filter(User.id == user_id).first()
    db.close()
    return result.current_chat_id

def update_user_last_chat_id(user_id: int, chat_id: int) -> Chat:
    db: Session = get_session()
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.current_chat_id = chat_id
    db.commit()
    db.close()
    return db_user
