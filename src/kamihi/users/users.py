"""
Common user-related functions.

License:
    MIT

"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from kamihi.db import BaseUser, Permission, RegisteredAction, get_engine


def get_users() -> Sequence[BaseUser]:
    """
    Get all users from the database.

    Returns:
        list[User]: A list of all users in the database.

    """
    with Session(get_engine()) as session:
        sta = select(BaseUser.cls())
        return session.execute(sta).scalars().all()


def get_user_from_telegram_id(telegram_id: int) -> BaseUser | None:
    """
    Get a user from the database using their Telegram ID.

    Args:
        telegram_id (int): The Telegram ID of the user.

    Returns:
        User | None: The user object if found, otherwise None.

    """
    with Session(get_engine()) as session:
        sta = select(BaseUser.cls()).where(BaseUser.cls().telegram_id == telegram_id)
        return session.execute(sta).scalars().first()


def is_user_authorized(user: BaseUser, action_name: str) -> bool:
    """
    Check if a user is authorized to use a specific action.

    Args:
        user (User): The user object to check.
        action_name (str): The action to check authorization for.

    Returns:
        bool: True if the user is authorized, False otherwise.

    """
    with Session(get_engine()) as session:
        user = session.get(BaseUser.cls(), user.id)

        if not user:
            return False

        if user.is_admin:
            return True

        sta = select(RegisteredAction).where(RegisteredAction.name == action_name)
        action = session.execute(sta).scalars().first()
        if action is None:
            mes = f"Action '{action_name}' is not registered in the database."
            raise ValueError(mes)

        sta = select(Permission).where(Permission.action == action)
        permissions = session.execute(sta).scalars().all()

        if not permissions:
            return False

        return any(permission.is_user_allowed(user) for permission in permissions)
