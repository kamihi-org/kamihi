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

from time import sleep
from typing import Any

from loguru import logger

from kamihi.base.config import KamihiSettings
from kamihi.base.logging import configure_logging


class Bot:
    """Bot class for Kamihi."""

    settings: KamihiSettings

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the Bot class.

        Args:
            **kwargs: Additional keyword arguments for settings.

        """
        self.settings = KamihiSettings(**kwargs)

    def set_settings(self, settings: KamihiSettings) -> None:
        """Set the settings for the bot."""
        self.settings = settings

    def start(self) -> None:
        """Start the bot."""
        configure_logging(logger, self.settings.log)

        logger.info("Starting bot...")

        while True:
            # Placeholder for bot's main loop
            logger.debug("Bot is running...")
            sleep(1)
