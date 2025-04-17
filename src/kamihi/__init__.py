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

__version__ = "0.4.0"

import sys

from kamihi.bot import Bot as _Bot

# Check if we're running under pytest
_running_tests = any("pytest" in arg for arg in sys.argv) or "pytest" in sys.modules

bot = None if _running_tests else _Bot()
