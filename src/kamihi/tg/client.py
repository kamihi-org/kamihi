"""
Telegram client module.

This module provides a Telegram client for sending messages and handling commands.

License:
    MIT

Examples:
    >>> from kamihi.tg.client import TelegramClient
    >>> from kamihi.base.config import KamihiSettings
    >>> client = TelegramClient(KamihiSettings())
    >>> client.run()

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    Defaults,
    DictPersistence,
    MessageHandler,
    filters,
)

from kamihi.base.config import KamihiSettings
from kamihi.tg.default_handlers import default, error

if TYPE_CHECKING:
    from kamihi.bot.action import Action


async def _post_init(_: Application) -> None:
    """Log the start of the bot."""
    logger.success("Started!")


async def _post_shutdown(_: Application) -> None:
    """Log the shutdown of the bot."""
    logger.success("Stopped!")


class TelegramClient:
    """
    Telegram client class.

    This class provides methods to send messages and handle commands.

    """

    _builder: ApplicationBuilder
    _app: Application

    def __init__(self, settings: KamihiSettings, actions: list[Action]) -> None:
        """
        Initialize the Telegram client.

        Args:
            settings (KamihiSettings): The settings object.
            actions (list[Action]): List of actions to register.

        """
        # Set up the application with all the settings
        self._builder = Application.builder()
        self._builder.token(settings.token)
        self._builder.defaults(
            Defaults(
                tzinfo=settings.timezone_obj,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        )
        self._builder.post_init(_post_init)
        self._builder.post_shutdown(_post_shutdown)
        self._builder.persistence(DictPersistence(bot_data_json=settings.model_dump_json()))

        # Build the application
        self._app: Application = self._builder.build()

        # Register the actions
        for action in actions:
            self._app.add_handler(action.handler)
            logger.trace(f"Handler for {action} registered")

        # Register the default handlers
        if settings.responses.default_enabled:
            self._app.add_handler(MessageHandler(filters.TEXT, default), group=1000)
        self._app.add_error_handler(error)

    def run(self) -> None:
        """Run the Telegram bot."""
        logger.trace("Starting main loop...")
        self._app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        logger.trace("Stopping main loop...")
        await self._app.stop()
