"""
Kamihi is a Python framework for creating Telegram bots.

This is a long description. It should be multiple lines and give an overview
of the package functionality. It should also mention the key features and
advantages of the package.

License:
    MIT

Attributes:
    __version__ (str): The version of the package.

"""

__version__ = "0.1.1"


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
