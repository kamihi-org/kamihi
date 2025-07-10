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
from telegram import BotCommand

from kamihi.base.config import KamihiSettings
from kamihi.db.mongo import connect, disconnect
from kamihi.templates import Templates
from kamihi.tg import TelegramClient
from kamihi.tg.handlers import AuthHandler
from kamihi.tg.media import Audio, Document, Location, Photo, Video, Voice
from kamihi.users import get_users, is_user_authorized
from kamihi.users.models import User
from kamihi.web import KamihiWeb

from .action import Action


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

    Document: Document = Document
    Photo: Photo = Photo
    Video: Video = Video
    Audio: Audio = Audio
    Location: Location = Location
    Voice: Voice = Voice

    _client: TelegramClient
    _web: KamihiWeb
    _actions: list[Action] = []

    def __init__(self, settings: KamihiSettings) -> None:
        """
        Initialize the Bot class.

        Args:
            settings: The settings for the bot.

        """
        self.settings = settings

        # Connects to the database
        connect(self.settings.db)

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

        # Create and store the action
        action = Action(func.__name__, commands, description, func)
        self._actions.append(action)

        # The action is returned so it can be used by the user if needed
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

    def user_class(self, cls: type[User]) -> None:  # skipcq: PYL-R0201
        """
        Set the user model for the bot.

        This method is used as a decorator to set the user model for the bot.

        Args:
            cls: The user class to set.

        """
        User.set_model(cls)

    @property
    def _valid_actions(self) -> list[Action]:
        """Return the valid actions for the bot."""
        return [action for action in self._actions if action.is_valid()]

    @property
    def _handlers(self) -> list[AuthHandler]:
        """Return the handlers for the bot."""
        return [action.handler for action in self._valid_actions]

    @property
    def _scopes(self) -> dict[int, list[BotCommand]]:
        """Return the current scopes for the bot."""
        scopes = {}
        for user in get_users():
            scopes[user.telegram_id] = []
            for action in self._valid_actions:
                if is_user_authorized(user, action.name):
                    scopes[user.telegram_id].extend(
                        [
                            BotCommand(command=command, description=action.description or f"Action {action.name}")
                            for command in action.commands
                        ]
                    )

        return scopes

    async def _set_scopes(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ARG002
        """
        Set the command scopes for the bot.

        This method sets the command scopes for the bot based on the registered
        actions.

        Args:
            *args: Positional arguments. Not used but required for using the method as a callback.
            **kwargs: Keyword arguments. Not used but required for using the method as a callback.

        """
        await self._client.set_scopes(self._scopes)

    async def _reset_scopes(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ARG002
        """
        Reset the command scopes for the bot.

        Args:
            *args: Positional arguments. Not used but required for using the method as a callback.
            **kwargs: Keyword arguments. Not used but required for using the method as a callback.

        """
        await self._client.reset_scopes(*args, **kwargs)

    def start(self) -> None:
        """Start the bot."""
        # Cleans up the database of actions that are not present in code
        Action.clean_up([action.name for action in self._actions])
        logger.debug("Removed actions not present in code from database")

        # Warns the user if there are no valid actions registered
        if not self._valid_actions:
            logger.warning("No valid actions were registered. The bot will not respond to any commands.")

        # Loads the Telegram client
        self._client = TelegramClient(self.settings, self._handlers)
        logger.trace("Initialized Telegram client")

        # Sets the command scopes for the bot
        self._client.register_run_once_job(self._reset_scopes, 1)
        self._client.register_run_once_job(self._set_scopes, 2)
        logger.trace("Initialized command scopes jobs")

        # Loads the web server
        self._web = KamihiWeb(
            self.settings.web,
            self.settings.db,
            {
                "after_create": [self._set_scopes],
                "after_edit": [self._set_scopes],
                "after_delete": [self._set_scopes],
            },
        )
        logger.trace("Initialized web server")
        self._web.start()

        # Loads the template engine
        self.templates = Templates(self.settings.autoreload_templates)
        logger.trace("Initialized templating engine")

        # Runs the client
        self._client.run()

        # When the client is stopped, stop the database connection
        disconnect()
