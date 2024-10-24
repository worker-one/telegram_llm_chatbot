from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, unique=True, primary_key=True, index=True)
    name = Column(String, index=True)

    # Establish relationship with Chat and enable cascade deletion
    chats = relationship("Chat", backref="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    name = Column(String)
    timestamp = Column(DateTime)

    # Establish relationship with Message and enable cascade deletion
    messages = relationship("Message", backref="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime)
