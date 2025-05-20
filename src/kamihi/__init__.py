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

__version__ = "0.8.0"

import os

from loguru import logger

from .base.config import KamihiSettings
from .base.logging import configure_logging as _configure_logging
from .bot import Bot as _Bot
from .users.models import User as BaseUser

if os.environ.get("PYTEST_VERSION") is None:
    # Load the settings and configure logging
    _settings = KamihiSettings()
    _configure_logging(logger, _settings.log)
    logger.trace("Initialized settings and logging")
    logger.bind(version=__version__).info("Starting Kamihi")

    # Initialize the bot
    bot = _Bot(_settings)

    __all__ = ["__version__", "bot", "KamihiSettings", "BaseUser"]
