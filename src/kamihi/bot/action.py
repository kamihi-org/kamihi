"""
Action helper class.

License:
    MIT

"""

from __future__ import annotations

import inspect
from collections.abc import Callable

import loguru
from loguru import logger
from telegram import Update
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CallbackContext, CommandHandler

from kamihi.tg.send import reply_text
from kamihi.utils import COMMAND_REGEX


class Action:
    """
    Action class for Kamihi bot.

    This class provides helpers for defining actions, their commands and their handlers.

    Attributes:
        name (str): The name of the action.
        commands (list[str]): List of commands associated.
        description (str): Description of the action.
        func (Callable): The function to be executed when the action is called.

    """

    name: str
    commands: list[str]
    description: str
    func: Callable

    _valid: bool = True
    _logger: loguru.Logger

    def __init__(self, name: str, commands: list[str], description: str, func: Callable) -> None:
        """
        Initialize the Action class.

        Args:
            name (str): The name of the action.
            commands (list[str]): List of commands associated.
            description (str): Description of the action.
            func (Callable): The function to be executed when the action is called.

        """
        self.name = name
        self.commands = commands
        self.description = description
        self.func = func

        self._logger = logger.bind(action=self.name)

        self._validate_commands()
        self._validate_function()

        if self.is_valid():
            self._logger.debug("Successfully registered")
        else:
            self._logger.warning("Failed to register")

    def _validate_commands(self) -> None:
        """Filter valid commands and log invalid ones."""
        min_len, max_len = BotCommandLimit.MIN_COMMAND, BotCommandLimit.MAX_COMMAND

        # Remove duplicate commands
        self.commands = list(set(self.commands))

        # Filter out invalid commands
        for cmd in self.commands.copy():
            if not COMMAND_REGEX.match(cmd):
                self._logger.warning(
                    "Command '/{cmd}' was discarded: "
                    "must be {min_len}-{max_len} chars of lowercase letters, digits and underscores",
                    cmd=cmd,
                    min_len=min_len,
                    max_len=max_len,
                )
                self.commands.remove(cmd)

        # Mark as invalid if no commands are left
        if not self.commands:
            self._logger.warning("No valid commands were given")
            self._valid = False

    def _validate_function(self) -> None:
        """Validate the function passed."""
        # Check if the function is a coroutine
        if not inspect.iscoroutinefunction(self.func):
            self._logger.warning(
                "Function should be a coroutine, define it with 'async def {name}()' instead of 'def {name}()'.",
                name=self.func.__name__,
            )
            self._valid = False

        # Check if the function has valid parameters
        parameters = inspect.signature(self.func).parameters
        for name, param in parameters.items():
            if name not in ("update", "context", "logger"):
                self._logger.warning(
                    "Invalid parameter '{name}' in function",
                    name=name,
                )
                self._valid = False

            if param.kind == inspect.Parameter.VAR_POSITIONAL or param.kind == inspect.Parameter.VAR_KEYWORD:
                self._logger.warning(
                    "Special arguments '*args' and '**kwargs' are not supported in action"
                    " parameters, they will be ignored. Beware that this may cause issues."
                )
                self._valid = False

    @property
    def handler(self) -> CommandHandler:
        """Construct a CommandHandler for the action."""
        return CommandHandler(self.commands, self.__call__) if self.is_valid() else None

    def is_valid(self) -> bool:
        """Check if the action is valid."""
        return self._valid

    async def __call__(self, update: Update, context: CallbackContext) -> None:
        """Execute the action."""
        if not self.is_valid():
            self._logger.warning("Not valid, skipping execution")
            return

        self._logger.debug("Executing")
        parameters = inspect.signature(self.func).parameters
        pos_args = []
        keyword_args = {}

        for name, param in parameters.items():
            match name:
                case "update":
                    value = update
                case "context":
                    value = context
                case "logger":
                    value = self._logger
                case _:
                    value = None

            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                pos_args.append(value)
            else:
                keyword_args[name] = value

        result = await self.func(*pos_args, **keyword_args)
        if result is not None:
            await reply_text(update, context, result)
        else:
            self._logger.debug("No result to send")

        self._logger.debug("Executed successfully")
        raise ApplicationHandlerStop

    def __repr__(self) -> str:
        """Return a string representation of the Action object."""
        return f"Action '{self.name}' ({', '.join(f'/{cmd}' for cmd in self.commands)}) [-> {self.func.__name__}]"
