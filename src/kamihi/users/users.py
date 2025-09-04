"""
Common user-related functions.

License:
    MIT

"""
from typing import Sequence

from sqlmodel import Session, select

from kamihi.db import Permission, RegisteredAction, User, get_engine


def get_users() -> Sequence[User]:
    """
    Get all users from the database.

    Returns:
        list[User]: A list of all users in the database.

    """
    with Session(get_engine()) as session:
        sta = select(User)
        return session.exec(sta).all()


def get_user_from_telegram_id(telegram_id: int) -> User | None:
    """
    Get a user from the database using their Telegram ID.

    Args:
        telegram_id (int): The Telegram ID of the user.

    Returns:
        User | None: The user object if found, otherwise None.

    """
    with Session(get_engine()) as session:
        sta = select(User).where(User.telegram_id == telegram_id)
        return session.exec(sta).first()


def is_user_authorized(user: User, action_name: str) -> bool:
    """
    Check if a user is authorized to use a specific action.

    Args:
        user (User): The user object to check.
        action_name (str): The action to check authorization for.

    Returns:
        bool: True if the user is authorized, False otherwise.

    """
    with Session(get_engine()) as session:
        user = session.get(User, user.id)

        if user.is_admin:
            return True

        sta = select(RegisteredAction).where(RegisteredAction.name == action_name)
        action = session.exec(sta).first()
        if action is None:
            raise ValueError(f"Action '{action_name}' is not registered in the database.")

        sta = select(Permission).where(Permission.action == action)
        permissions = session.exec(sta).all()

        if not permissions:
            return False

        return any([permission.is_user_allowed(user) for permission in permissions])
