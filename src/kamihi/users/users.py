"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]

"""

from mongoengine import Q

from kamihi.bot.models import RegisteredAction

from .models import Role, User
from .models.permission import Permission


def get_users() -> list[User]:
    """
    Get all users from the database.

    Returns:
        list[User]: A list of all users in the database.

    """
    return User.objects()


def get_user_from_telegram_id(telegram_id: int) -> User | None:
    """
    Get a user from the database using their Telegram ID.

    Args:
        telegram_id (int): The Telegram ID of the user.

    Returns:
        User | None: The user object if found, otherwise None.

    """
    return User.objects(telegram_id=telegram_id).first()


def is_user_authorized(user: User, action: str) -> bool:
    """
    Check if a user is authorized tu use a specific action.

    Args:
        user (User): The user object to check.
        action (str): The action to check authorization for.

    Returns:
        bool: True if the user is authorized, False otherwise.

    """
    action = RegisteredAction.objects(name=action).first()
    role = Role.objects(users=user).first()
    permissions = Permission.objects(Q(action=action) & (Q(users=user) | Q(roles=role))).first()

    return bool(permissions)
