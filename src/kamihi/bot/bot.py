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
from collections.abc import Callable
from functools import partial
from typing import Any

from loguru import logger
from multipledispatch import dispatch

from kamihi.base.config import KamihiSettings
from kamihi.base.logging import configure_logging
from kamihi.bot.action import Action
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
    _actions: list[Action] = []

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        """
        Initialize the Bot class.

        Args:
            **kwargs: Additional keyword arguments for settings.

        """
        # Loads the settings
        self.settings = KamihiSettings(**kwargs)

    @dispatch([(str, Callable)])
    def action(self, *args: str | Callable, description: str = None) -> Action | Callable:
        """
        Register an action with the bot.

        The commands in `*args` must be unique and can only contain lowercase letters,
        numbers, and underscores. Do not prepend the commands with a slash, as it
        will be added automatically.

        Args:
            *args: A list of command names. If not provided, the function name will be used.
            description: A description for the action. This will be used in the help message.

        Returns:
            Callable: The wrapped function.

        """
        # Because of the dispatch decorator, the function is passed as the last argument
        args = list(args)
        func: Callable = args.pop()
        commands: list[str] = args or [func.__name__]

        action = Action(func.__name__, commands, description, func)

        self._actions.append(action)

        return action

    @dispatch([str])
    def action(self, *commands: str, description: str = "") -> partial[Action]:
        """
        Register an action with the bot.

        This method overloads the `bot.action` method so the decorator can be used
        with or without parentheses.

        Args:
            *commands: A list of command names. If not provided, the function name will be used.
            description: A description of the action. This will be used in the help message.

        Returns:
            Callable: The wrapped function.

        """
        return functools.partial(self.action, *commands, description=description)

    def on_message(self, regex: str = None) -> Callable: ...  # noqa: D102

    def start(self) -> None:
        """Start the bot."""
        # Configures the logging
        configure_logging(logger, self.settings.log)
        logger.trace("Logging configured")

        # Loads the templates
        self.templates = Templates(self.settings.autoreload_templates)
        logger.trace("Templates initialized")

        # Loads the Telegram client
        self._client = TelegramClient(self.settings, self._actions)
        logger.trace("Telegram client initialized")

        # Runs the client
        self._client.run()
