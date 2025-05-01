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

__version__ = "0.5.2"


from loguru import logger

from kamihi.base.config import KamihiSettings
from kamihi.base.logging import configure_logging
from kamihi.bot import Bot as _Bot

# Load the settings and configure logging
_settings = KamihiSettings()
configure_logging(logger, _settings.log)
logger.trace("Settings and logging initialized.")

# Initialize the bot
bot = _Bot(_settings)


__all__ = ["bot"]
