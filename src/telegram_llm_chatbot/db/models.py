from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base model"""

    pass


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(BigInteger, unique=True, primary_key=True, index=True)
    name = Column(String, index=True)
    current_chat_id = Column(Integer)

    # Establish relationship with Chat and enable cascade deletion
    chats = relationship("Chat", backref="user", cascade="all, delete-orphan")


class Chat(Base):
    """Chat model"""

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    name = Column(String)
    timestamp = Column(DateTime)

    # Establish relationship with Message and enable cascade deletion
    messages = relationship("Message", backref="chat", cascade="all, delete-orphan")


class Message(Base):
    """Message model"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime)
