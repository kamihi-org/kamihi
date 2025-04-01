"""
Kamihi is a Python framework for creating and managing Telegram bots.

Examples:
    >>> from kamihi import bot
    >>> bot.start()

License:
    MIT

Attributes:
    __version__ (str): The version of the package.
    bot (Bot): The bot instance for the Kamihi framework. Preferable to using the
        Bot class directly, as it ensures that the bot is properly configured and
        managed by the framework.

"""

__version__ = "0.3.0"

from kamihi.bot import Bot as _Bot

bot = _Bot()
