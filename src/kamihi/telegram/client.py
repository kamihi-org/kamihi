"""
Telegram client module.

This module provides a Telegram client for sending messages and handling commands.

License:
    MIT

Examples:
    >>> from kamihi.telegram.client import TelegramClient
    >>> from pytz import timezone
    >>> client = TelegramClient("my_token", timezone("UTC"))
    >>> client.run()

"""

import re

from loguru import logger
from telegram import Update
from telegram.constants import BotCommandLimit, ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    Defaults,
    DictPersistence,
    MessageHandler,
    filters,
)

from kamihi.base.config import KamihiSettings
from kamihi.telegram.default_handlers import default, error


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
    _command_regex = re.compile(rf"^[a-z0-9_]{{{BotCommandLimit.MIN_COMMAND},{BotCommandLimit.MAX_COMMAND}}}$")

    def __init__(self, settings: KamihiSettings) -> None:
        """
        Initialize the Telegram client.

        Args:
            settings (KamihiSettings): The settings object.

        """
        self._builder = Application.builder()
        self._builder.token(settings.token)
        self._builder.defaults(
            Defaults(
                tzinfo=settings.timezone,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        )
        self._builder.post_init(_post_init)
        self._builder.post_shutdown(_post_shutdown)
        self._builder.persistence(DictPersistence(bot_data_json=settings.model_dump_json()))

        self._app: Application = self._builder.build()

        self._app.add_handler(MessageHandler(filters.ALL, default), group=1000)
        self._app.add_error_handler(error)

    def _filter_valid_commands(self, commands: list[str], callback_name: str) -> list[str]:
        """Filter valid commands and log invalid ones."""
        min_len, max_len = BotCommandLimit.MIN_COMMAND, BotCommandLimit.MAX_COMMAND
        valid_commands = []

        for cmd in commands:
            if not self._command_regex.match(cmd):
                logger.warning(
                    f"Command {cmd} for {callback_name} was discarded: "
                    f"must be {min_len}-{max_len} chars of lowercase letters, digits and underscores"
                )
                continue
            if cmd in valid_commands:
                logger.warning(f"Command '{cmd}' for {callback_name} was discarded: already registered")
                continue
            valid_commands.append(cmd)

        return valid_commands

    async def register_command(self, command: str | list[str], callback) -> None:  # noqa: ANN001
        """
        Register a command handler.

        Args:
            command (str | list[str]): The command(s) to register.
            callback: The callback function to handle the command.

        """
        if isinstance(command, str):
            command = [command]

        valid_commands = self._filter_valid_commands(command, callback.__name__)

        if not valid_commands:
            logger.warning(f"No valid commands provided for {callback.__name__}")
            return

        self._app.add_handler(CommandHandler(valid_commands, callback))
        logger.debug(f"command(s) {', '.join('/' + cmd for cmd in command)} registered")

    def run(self) -> None:
        """Run the Telegram bot."""
        logger.debug("Starting main loop...")
        self._app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        logger.debug("Stopping main loop...")
        await self._app.stop()
