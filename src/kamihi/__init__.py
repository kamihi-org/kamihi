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

from loguru import logger

from .base.config import KamihiSettings
from .base.logging import configure_logging
from .bot import Bot
from .users.models import User as BaseUser

__version__ = "1.2.0"


bot: Bot


def _init_bot(settings: KamihiSettings) -> Bot:
    """Start the Kamihi bot."""
    global bot  # skipcq: PYL-W0603

    configure_logging(logger, settings.log)
    logger.trace("Initialized settings and logging")

    bot = Bot(settings)
    return bot


__all__ = ["__version__", "bot", "KamihiSettings", "BaseUser"]
