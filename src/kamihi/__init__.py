"""
Kamihi.

Kamihi is a Python package for creating and managing Telegram bots.
"""

__version__ = "0.1.0"


def hello(name: str) -> str:
    """
    Say hello to the user.

    Examples:
        >>> hello("Alice")
        "Hello from Kamihi, Alice!"
        >>> hello("Bob")
        "Hello from Kamihi, Bob!"

    Args:
        name: The name of the user.

    Returns:
        The greeting message.

    """
    return f"Hello from Kamihi, {name}!"
