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

import functools
from collections.abc import Callable, Coroutine
from functools import partial
from typing import Any

import wrapt
from loguru import logger
from multipledispatch import dispatch
from telegram.error import TelegramError

from kamihi.base.config import KamihiSettings
from kamihi.base.logging import configure_logging
from kamihi.templates import Templates
from kamihi.tg import TelegramClient


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
        templates (Templates): The templates loaded by the bot.

    """

    settings: KamihiSettings
    templates: Templates

    _client: TelegramClient
    _commands: list[dict[str, str | Callable]] = []

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the Bot class.

        Args:
            **kwargs: Additional keyword arguments for settings.

        """
        # Loads the settings
        self.settings = KamihiSettings(**kwargs)

    @dispatch([(str, Callable)])
    def command(self, *commands: str, description: str = None) -> Coroutine:
        """
        Register a command with the bot.

        The command name must be unique and can only contain lowercase letters,
        numbers, and underscores. Do not prepend the command with a slash, as it
        will be added automatically.

        Args:
            *commands: A list of command names. If not provided, the function name will be used.
            description: A description of the command. This will be used in the help message.

        Returns:
            Coroutine: The wrapped function.

        """
        commands = list(commands)
        _func = commands.pop()
        self._save_command(self._call_command(_func), commands or [_func.__name__], description=description)
        return self._call_command(_func)

    @dispatch([str])
    def command(self, *commands: str, description: str = "") -> partial[Coroutine]:
        """
        Register a command with the bot.

        This method overloads the command method so the decorator can be used
        with or without parentheses.

        Args:
            *commands: A list of command names. If not provided, the function name will be used.
            description: A description of the command. This will be used in the help message.

        Returns:
            Coroutine: The wrapped function.

        """
        return functools.partial(self.command, *commands, description=description)

    def _save_command(self, func: Coroutine, commands: list[str], description: str = "") -> None:
        """Save a command for registration on startup."""
        self._commands.append({"commands": commands, "description": description, "func": func})

    @wrapt.decorator
    async def _call_command(self, func: Callable, instance: Any, args: tuple, kwargs: dict) -> None:  # noqa: ANN401, ARG002
        """Call a command with the bot."""
        result = await func()
        await self._client.reply(*args, result)

    def action(self, *commands: str, description: str = "") -> Callable: ...  # noqa: D102

    def on_message(self, regex: str = None) -> Callable: ...  # noqa: D102

    def _register_commands(self) -> None:
        """Register all commands."""
        for command in self._commands:
            with logger.catch(
                exception=TelegramError,
                message=f"Error registering command {command['commands']}",
            ):
                self._client.register_command(command["commands"], command["func"])
                logger.debug(f"Registered command: {command['commands']}")

    def start(self) -> None:
        """Start the bot."""
        # Configures the logging
        configure_logging(logger, self.settings.log)
        logger.trace("Logging configured")

        # Loads the templates
        self.templates = Templates(self.settings.autoreload_templates)
        logger.trace("Templates initialized")

        # Loads the Telegram client
        self._client = TelegramClient(self.settings)
        logger.trace("Telegram client initialized")

        # Registers the commands
        self._register_commands()
        logger.trace("Commands registered")

        # Runs the client
        self._client.run()
