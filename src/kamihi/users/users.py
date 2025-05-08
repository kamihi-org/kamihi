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

from .models import User


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
