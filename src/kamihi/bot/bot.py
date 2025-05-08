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

from loguru import logger
from multipledispatch import dispatch
from telegram.ext import CommandHandler

from kamihi.base.config import KamihiSettings
from kamihi.bot.action import Action
from kamihi.db.db import connect_to_db
from kamihi.db.models.user import User
from kamihi.templates import Templates
from kamihi.tg import TelegramClient
from kamihi.web.web import KamihiWeb


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
    _web: KamihiWeb
    _actions: list[Action]

    def __init__(self, settings: KamihiSettings) -> None:
        """
        Initialize the Bot class.

        Args:
            settings: The settings for the bot.

        """
        self.settings = settings
        self._actions = []

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
    def action(self, *commands: str, description: str = None) -> partial[Action]:
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

    @property
    def valid_actions(self) -> list[Action]:
        """Return the valid actions for the bot."""
        return [action for action in self._actions if action.is_valid()]

    @property
    def _handlers(self) -> list[CommandHandler]:
        """Return the handlers for the bot."""
        return [action.handler for action in self.valid_actions]

    def user_class(self, cls: type[User]) -> None:
        """
        Set the user class for the bot.

        Args:
            cls: The user class to set.

        """
        User.set_model(cls)

    def start(self) -> None:
        """Start the bot."""
        # Connects to the database
        connect_to_db(self.settings)

        # Loads the templates
        self.templates = Templates(self.settings.autoreload_templates)
        logger.trace("Templates initialized")

        # Warns the user if there are no valid actions registered
        if not self.valid_actions:
            logger.warning("No valid actions were registered. The bot will not respond to any commands.")

        # Loads the Telegram client
        self._client = TelegramClient(self.settings, self._handlers)
        logger.trace("Telegram client initialized")

        # Loads the web server
        self._web = KamihiWeb(self.settings)
        logger.trace("Web server initialized")
        self._web.start()

        # Runs the client
        self._client.run()
