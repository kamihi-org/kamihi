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

from loguru import logger
from telegram import BotCommand, BotCommandScopeChat, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    BaseHandler,
    CallbackContext,
    Defaults,
    DictPersistence,
    MessageHandler,
    filters,
)

from kamihi.base.config import KamihiSettings

from .default_handlers import default, error


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

    _bot_settings: KamihiSettings
    _base_url: str = "https://api.telegram.org/bot"
    _builder: ApplicationBuilder
    _app: Application

    def __init__(self, settings: KamihiSettings, handlers: list[BaseHandler]) -> None:
        """
        Initialize the Telegram client.

        Args:
            settings (KamihiSettings): The settings object.
            handlers (list[BaseHandler]): List of handlers to register.

        """
        self._bot_settings = settings

        if self._bot_settings.testing:
            self._base_url = "https://api.telegram.org/bot{token}/test"

        # Set up the application with all the settings
        self._builder = Application.builder()
        self._builder.base_url(self._base_url)
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

        # Register the handlers
        for handler in handlers:
            with logger.catch(exception=TelegramError, message="Failed to register handler"):
                self._app.add_handler(handler)

        # Register the default handlers
        if settings.responses.default_enabled:
            self._app.add_handler(MessageHandler(filters.TEXT, default), group=1000)
        self._app.add_error_handler(error)

    async def reset_scopes(self, context: CallbackContext) -> None:  # noqa: ARG002
        """
        Reset the command scopes for the bot.

        This method clears all command scopes and sets the default commands.

        Args:
            context (CallbackContext): The context of the callback. Not used but required for
                this function to be registered as a job.

        """
        if self._bot_settings.testing:
            logger.debug("Testing mode, skipping resetting scopes")
            return

        with logger.catch(exception=TelegramError, message="Failed to reset scopes"):
            await self._app.bot.set_my_commands(commands=[])
            logger.debug("Scopes erased")

    async def set_scopes(self, scopes: dict[int, list[BotCommand]]) -> None:
        """
        Set the command scopes for the bot.

        Args:
            scopes (dict[int, list[BotCommand]]): The command scopes to set.

        """
        if self._bot_settings.testing:
            logger.debug("Testing mode, skipping setting scopes")
            return

        for user_id, commands in scopes.items():
            lg = logger.bind(user_id=user_id, commands=[command.command for command in commands])
            with lg.catch(
                exception=TelegramError,
                message="Failed to set scopes for user {user_id}",
            ):
                await self._app.bot.set_my_commands(
                    commands=commands,
                    scope=BotCommandScopeChat(user_id),
                )
                lg.debug("Scopes set")

    def register_run_once_job(self, callback: callable, when: int) -> None:
        """
        Add a job to run once.

        Args:
            callback (callable): The callback function to run.
            when (int): second from now to run the job.

        """
        self._app.job_queue.run_once(callback, when)

    def run(self) -> None:
        """Run the Telegram bot."""
        logger.trace("Starting main loop...")
        self._app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        logger.trace("Stopping main loop...")
        await self._app.stop()
