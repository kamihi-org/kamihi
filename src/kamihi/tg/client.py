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

import re
from collections.abc import Callable

from loguru import logger
from telegram import Update
from telegram.constants import BotCommandLimit, ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    Defaults,
    DictPersistence,
    MessageHandler,
    filters,
)

from kamihi.base.config import KamihiSettings
from kamihi.tg.default_handlers import default, error
from kamihi.tg.send import reply_text, send_text


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
    _registered_commands: set[str] = set()

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
                tzinfo=settings.timezone_obj,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        )
        self._builder.post_init(_post_init)
        self._builder.post_shutdown(_post_shutdown)
        self._builder.persistence(DictPersistence(bot_data_json=settings.model_dump_json()))

        self._app: Application = self._builder.build()

        if settings.responses.default_enabled:
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
            if cmd in valid_commands or cmd in self._registered_commands:
                logger.warning(f"Command '{cmd}' for {callback_name} was discarded: already registered")
                continue
            valid_commands.append(cmd)

        return valid_commands

    def register_command(self, command: str | list[str], callback: Callable) -> None:  # noqa: ANN001
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
        self._registered_commands.update(valid_commands)
        logger.debug(f"command(s) {', '.join('/' + cmd for cmd in command)} registered")

    def run(self) -> None:
        """Run the Telegram bot."""
        logger.trace("Starting main loop...")
        self._app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        logger.trace("Stopping main loop...")
        await self._app.stop()

    async def send(self, chat_id: int, message: str) -> None:
        """
        Send a message to a chat.

        Args:
            chat_id (int): The ID of the chat to send the message to.
            message (str): The text of the message.

        """
        await send_text(self._app.bot, chat_id, message)

    async def reply(self, update: Update, context: CallbackContext, message: str) -> None:
        """
        Reply to a message.

        Args:
            update: The Update object passed by the handler.
            context: The CallbackContext object passed by the handler.
            message (str): The text of the reply.

        """
        await reply_text(update, context, message)
