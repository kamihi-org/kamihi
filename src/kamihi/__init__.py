"""
Kamihi.

Kamihi is a Python package for creating and managing Telegram bots.
"""

__version__ = "0.1.0"


def hello(name: str) -> str:
    """
    Say hello to the user.

    Args:
        name (str): The name of the user.

    Returns:
        str: The greeting message.

    """
    return f"Hello from Kamihi, {name}!"
