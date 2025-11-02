"""
Telegram client module.

This module provides a Telegram client for sending messages and handling commands.

License:
    MIT

Examples:
    >>> from kamihi.tg.client import TelegramClient
    >>> from kamihi.base.config import KamihiSettings
    >>> client = TelegramClient(KamihiSettings(), [])
    >>> client.run()

"""

from __future__ import annotations

from collections.abc import Callable

from loguru import logger
from telegram import BotCommand, BotCommandScopeChat, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    BaseHandler,
    Defaults,
    MessageHandler,
    filters,
)

from kamihi.base import get_settings

from .default_handlers import default, error


class TelegramClient:
    """
    Telegram client class.

    This class provides methods to send messages and handle commands.

    """

    app: Application
    _base_url: str = "https://api.telegram.org/bot"
    _base_file_url: str = "https://api.telegram.org/file/bot"
    _builder: ApplicationBuilder
    _testing: bool = False

    def __init__(self, handlers: list[BaseHandler], _post_init: Callable, _post_shutdown: Callable) -> None:
        """
        Initialize the Telegram client.

        Args:
            handlers (list[BaseHandler]): List of handlers to register.
            _post_init (callable): Function to call after the application is initialized.
            _post_shutdown (callable): Function to call after the application is shut down.

        """
        settings = get_settings()

        if settings.testing:
            self._base_url = "https://api.telegram.org/bot{token}/test"
            self._base_file_url = "https://api.telegram.org/file/bot{token}/test"
            self._testing = True

        # Set up the application with all the settings
        self._builder = Application.builder()
        self._builder.base_url(self._base_url)
        self._builder.base_file_url(self._base_file_url)
        self._builder.token(settings.token)
        self._builder.defaults(
            Defaults(
                tzinfo=settings.timezone_obj,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        )
        self._builder.post_init(_post_init)
        self._builder.post_shutdown(_post_shutdown)

        # Build the application
        self.app: Application = self._builder.build()

        # Register the handlers
        for handler in handlers:
            with logger.catch(exception=TelegramError, level="ERROR", message="Failed to register handler"):
                self.app.add_handler(handler)

        # Register the default handlers
        with logger.catch(exception=TelegramError, level="ERROR", message="Failed to register default handlers"):
            if settings.responses.default_enabled:
                self.app.add_handler(MessageHandler(filters.TEXT, default))
            self.app.add_error_handler(error)

    async def reset_scopes(self) -> None:  # noqa: ARG002
        """
        Reset the command scopes for the bot.

        This method clears all command scopes and sets the default commands.
        """
        if self._testing:
            logger.debug("Testing mode, skipping resetting scopes")
            return

        with logger.catch(exception=TelegramError, message="Failed to reset scopes"):
            await self.app.bot.delete_my_commands()
            logger.debug("Scopes erased")

    async def set_scopes(self, scopes: dict[int, list[BotCommand]]) -> None:
        """
        Set the command scopes for the bot.

        Args:
            scopes (dict[int, list[BotCommand]]): The command scopes to set.

        """
        if self._testing:
            logger.debug("Testing mode, skipping setting scopes")
            return

        for user_id, commands in scopes.items():
            lg = logger.bind(user_id=user_id, commands=[command.command for command in commands])
            with lg.catch(
                exception=TelegramError,
                message="Failed to set scopes",
            ):
                await self.app.bot.set_my_commands(
                    commands=commands,
                    scope=BotCommandScopeChat(user_id),
                )
                lg.debug("Scopes set")

    def run(self) -> None:
        """Run the Telegram bot."""
        logger.trace("Starting main loop...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        logger.trace("Stopping main loop...")
        await self.app.stop()
