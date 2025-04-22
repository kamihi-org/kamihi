"""
Bot module for Kamihi.

This module provides the primary interface for the Kamihi framework, allowing
for the creation and management of Telegram bots.

The framework already provides a bot instance, which can be accessed using the
`bot` variable. This instance is already configured with default settings and
can be used to start the bot. The managed instance is preferable to using the
`Bot` class directly, as it ensures that the bot is properly configured and
managed by the framework.

License:
    MIT

Examples:
    >>> from kamihi import bot
    >>> bot.start()

"""

import os
from collections.abc import Callable
from pathlib import Path
from time import sleep
from typing import Any

from loguru import logger

from kamihi.base.config import KamihiSettings
from kamihi.base.logging import configure_logging
from kamihi.templates import Templates


class Bot:
    """
    Bot class for Kamihi.

    The framework already provides a bot instance, which can be accessed using the
    `bot` variable. This instance is already configured with default settings and
    can be used to start the bot. The managed instance is preferable to using the
    `Bot` class directly, as it ensures that the bot is properly configured and
    managed by the framework.

    Attributes:
        settings (KamihiSettings): The settings for the bot.

    """

    settings: KamihiSettings
    templates: Templates

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the Bot class.

        Args:
            **kwargs: Additional keyword arguments for settings.

        """
        self.settings = KamihiSettings(**kwargs)
        self.templates = Templates(self.settings.autoreload_templates)

    def set_settings(self, settings: KamihiSettings) -> None:
        """Set the settings for the bot."""
        self.settings = settings

    def add_settings(self, settings: dict[str, Any] | KamihiSettings) -> None: ...  # noqa: D102

    def replace_settings(self, settings: dict[str, Any] | KamihiSettings) -> None: ...  # noqa: D102

    def action(self, *commands: str, description: str = "") -> Callable: ...  # noqa: D102

    def command(self, *commands: str, description: str = "") -> Callable: ...  # noqa: D102

    def on_message(self, regex: str = None) -> Callable: ...  # noqa: D102

    def start(self) -> None:
        """Start the bot."""
        configure_logging(logger, self.settings.log)

        logger.info("Starting bot...")

        while True:
            # Placeholder for bot's main loop
            logger.debug("Bot is running...")
            sleep(1)
