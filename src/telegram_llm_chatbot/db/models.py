from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base model"""

    pass


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(BigInteger, unique=True, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String, default="user")
    current_chat_id = Column(Integer)

    # Establish relationship with Chat and enable cascade deletion
    chats = relationship("Chat", backref="user", cascade="all, delete-orphan")

    # Establish relationship with Subscription and enable cascade deletion
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


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


class Log(Base):
    """Log model"""

    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    content = Column(String)
    timestamp = Column(DateTime)

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2))
    currency = Column(String, default="USD")
    duration_in_days = Column(Integer)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum("active", "inactive", "canceled", name="subscription_status"))

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

    # Establish relationship with Payment and enable cascade deletion
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(Numeric(10, 2))
    currency = Column(String)
    payment_date = Column(DateTime)
    payment_method = Column(String)

    subscription = relationship("Subscription", back_populates="payments")

User.subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")