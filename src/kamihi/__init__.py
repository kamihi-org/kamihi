"""
Kamihi is a Python framework for creating and managing Telegram bots.

License:
    MIT

Attributes:
    __version__ (str): The version of the package.
    bot (Bot): The bot instance for the Kamihi framework. Preferable to using the
        Bot class directly, as it ensures that the bot is properly configured and
        managed by the framework.

"""

import typing

if typing.TYPE_CHECKING:
    from .bot import Bot

__version__ = "5.4.0"


bot: "Bot"


def init_bot() -> "Bot":
    """Start the Kamihi bot."""
    global bot  # skipcq: PYL-W0603

    from .bot import Bot

    bot = Bot()
    return bot


__all__ = ["__version__", "bot"]
