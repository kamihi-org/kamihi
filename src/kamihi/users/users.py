"""
Common user-related functions.

License:
    MIT

"""

from mongoengine import Q

from kamihi.bot.models import RegisteredAction

from .models import Permission, Role, User


def get_users() -> list[User]:
    """
    Get all users from the database.

    Returns:
        list[User]: A list of all users in the database.

    """
    return list(User.objects)


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
    Check if a user is authorized to use a specific action.

    Args:
        user (User): The user object to check.
        action (str): The action to check authorization for.

    Returns:
        bool: True if the user is authorized, False otherwise.

    """
    if user.is_admin:
        return True

    action = RegisteredAction.objects(name=action).first()
    role = Role.objects(users=user).first()
    permissions = Permission.objects(Q(action=action) & (Q(users=user) | Q(roles=role))).first()

    return bool(permissions)
