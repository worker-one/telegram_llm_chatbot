import logging
from typing import Optional

from sqlalchemy.orm import Session

from .models import User

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()

def add_user(db: Session, user_id: int, username: str, last_chat_id: int = None):
	new_user = User(
		user_id=user_id,
		username=username,
        last_chat_id=last_chat_id
	)
	# add only if the user is not already in the database
	if not db.query(User).filter(User.user_id == user_id).first():
		db.add(new_user)
	db.commit()


def update_user(
        db: Session,
        user_id: int,
        username: str,
        last_chat_id: Optional[int] = None
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.username = username
        user.last_chat_id = last_chat_id
        logger.info(f"User with id {user_id} updated successfully.")
        db.commit()
    else:
        logger.error(f"User with id {user_id} not found in the database.")

def get_last_chat_id(
        db: Session,
        user_id: int
):
    user = db.query(User).filter(User.user_id == user_id).first()
    db.commit()
    if user:
        return user.last_chat_id
    else:
        logger.error(f"User with id {user_id} not found in the database.")
        return None
