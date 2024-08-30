from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages_telegram_llm_chatbot'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    user_id = Column(Integer)
    message_text = Column(String)


class User(Base):
    __tablename__ = 'users_telegram_llm_chatbot'

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    last_chat_id = Column(Integer)
