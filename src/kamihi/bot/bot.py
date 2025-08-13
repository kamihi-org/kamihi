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
from telegram import BotCommand
from telegram.ext import Application

from kamihi.base.config import KamihiSettings
from kamihi.datasources import DataSource
from kamihi.db.mongo import connect, disconnect
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

    """

    settings: KamihiSettings
    datasources: dict[str, DataSource] = {}

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

        # Loads the datasources
        for datasource_config in self.settings.datasources:
            datasource_class = DataSource.get_datasource_class(datasource_config.type)
            try:
                self.datasources[datasource_config.name] = datasource_class(datasource_config)
            except ImportError as e:
                msg = (
                    f"Failed to initialize data source '{datasource_config.name}' "
                    f"of type '{datasource_config.type}' because of missing dependencies."
                )
                raise ImportError(msg) from e

            logger.trace("Initialized", datasource=datasource_config.name, type=datasource_config.type)

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

        name = func.__name__
        commands: list[str] = args or [func.__name__]

        # Create and store the action
        try:
            action = Action(name, commands, description, func, datasources=self.datasources)
        except ValueError:
            logger.bind(action=name).exception("Failed to register action")
            return func

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

    @staticmethod
    def user_class(user_class: type[User]) -> type[User]:
        """
        Set the user model for the bot.

        This method is used as a decorator to set the user model for the bot.

        Args:
            user_class: The user class to set.

        """
        User.set_model(user_class)
        return user_class

    @property
    def _handlers(self) -> list[AuthHandler]:
        """Return the handlers for the bot."""
        return [action.handler for action in self._actions]

    @property
    def _scopes(self) -> dict[int, list[BotCommand]]:
        """Return the current scopes for the bot."""
        scopes = {}
        for user in get_users():
            scopes[user.telegram_id] = []
            for action in self._actions:
                if is_user_authorized(user, action.name):
                    scopes[user.telegram_id].extend(
                        [
                            BotCommand(command=command, description=action.description or f"Action {action.name}")
                            for command in action.commands
                        ]
                    )

        return scopes

    async def _set_scopes(self, *_args: Any) -> None:  # noqa: ANN401
        """Set the command scopes for the bot."""
        await self._client.set_scopes(self._scopes)

    async def _reset_scopes(self, *_args: Any) -> None:  # noqa: ANN401
        """Reset the command scopes for the bot."""
        await self._client.reset_scopes()

    # skipcq: TCV-001
    def start(self) -> None:
        """Start the bot."""
        # Cleans up the database of actions that are not present in code
        Action.clean_up([action.name for action in self._actions])
        logger.debug("Removed actions not present in code from database")

        # Warns the user if there are no valid actions registered
        if not self._actions:
            logger.warning("No valid actions were registered. The bot will not respond to any commands.")

        # Loads the Telegram client
        self._client = TelegramClient(self.settings, self._handlers, self._post_init, self._post_shutdown)
        logger.trace("Initialized Telegram client")

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

        # Runs the client
        self._client.run()

        # When the client is stopped, stop the database connection
        disconnect()
        logger.trace("Disconnected from the database")

    async def _post_init(self, _: Application) -> None:
        """
        Post-initialization callback for the bot.

        This method is called after the bot application is initialized. It sets
        the command scopes and registers the handlers.
        """
        # Sets the command scopes for the bot
        await self._reset_scopes()
        await self._set_scopes()
        logger.trace("Set command scopes")

        # Connects to the datasources
        for datasource in self.datasources.values():
            await datasource.connect()

        # Logs successful startup
        logger.success("Bot started")

    async def _post_shutdown(self, _: Application) -> None:
        """
        Post-shutdown callback for the bot.

        This method is called after the bot application is shut down. It cleans
        up the database and disconnects from the datasources.
        """
        disconnect()
        logger.trace("Disconnected from the database")

        # Disconnects from the datasources
        for datasource in self.datasources.values():
            await datasource.disconnect()

        # Logs successful shutdown
        logger.success("Bot stopped")
