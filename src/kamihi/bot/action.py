"""
Action helper class.

License:
    MIT

"""

from __future__ import annotations

import inspect
import pathlib
import typing
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any

import loguru
from loguru import logger
from telegram import Update
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CallbackContext, CommandHandler

from kamihi.bot.media import Photo
from kamihi.tg import send_document, send_text
from kamihi.tg.handlers import AuthHandler
from kamihi.tg.send import send_photo
from kamihi.users import get_user_from_telegram_id

from .models import RegisteredAction
from .utils import COMMAND_REGEX, parse_annotation


class Action:
    """
    Action class for Kamihi bot.

    This class provides helpers for defining actions, their commands and their handlers.

    Attributes:
        name (str): The name of the action.
        commands (list[str]): List of commands associated.
        description (str): Description of the action.

    """

    name: str
    commands: list[str]
    description: str

    _func: Callable
    _valid: bool = True
    _logger: loguru.Logger
    _db_object: RegisteredAction | None

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

        self._func = func
        self._logger = logger.bind(action=self.name)

        self._validate_commands()
        self._validate_function()

        if self.is_valid():
            self._db_object = self.save_to_db()
            self._logger.debug("Successfully registered")
        else:
            self._db_object = None
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
        if not inspect.iscoroutinefunction(self._func):
            self._logger.warning(
                "Function should be a coroutine, define it with 'async def {name}()' instead of 'def {name}()'.",
                name=self._func.__name__,
            )
            self._valid = False

        # Check if the function has valid parameters
        parameters = inspect.signature(self._func).parameters
        for name, param in parameters.items():
            if name not in ("update", "context", "logger", "user"):
                self._logger.warning(
                    "Invalid parameter '{name}' in function",
                    name=name,
                )
                self._valid = False

            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                self._logger.warning(
                    "Special arguments '*args' and '**kwargs' are not supported in action"
                    " parameters, they will be ignored. Beware that this may cause issues."
                )
                self._valid = False

    @property
    def handler(self) -> AuthHandler:
        """Construct a CommandHandler for the action."""
        return AuthHandler(CommandHandler(self.commands, self.__call__), self.name) if self.is_valid() else None

    def is_valid(self) -> bool:
        """Check if the action is valid."""
        return self._valid

    def save_to_db(self) -> RegisteredAction:
        """Save the action to the database."""
        return RegisteredAction.objects(name=self.name).upsert_one(
            name=self.name,
            description=self.description,
        )

    @classmethod
    def clean_up(cls, keep: list[str]) -> None:
        """Clean up the action from the database."""
        RegisteredAction.objects(name__nin=keep).delete()

    def _validate_result(self, result: Any) -> bool:  # noqa: ANN401
        """Validate the result of the action."""
        ann_type, ann_metadata = parse_annotation(inspect.signature(self._func).return_annotation)

        if ann_type and not isinstance(result, ann_type):
            self._logger.error(
                "Action returned an unexpected type: expected {expected}, got {actual}",
                expected=ann_type,
                actual=type(result),
            )
            return False
        if not ann_type and result is not None:
            self._logger.warning(
                "Action returned a value of type {typ} but no return type annotation was specified",
                typ=type(result),
            )

        return True

    async def _send_result(self, result: Any, update: Update, context: CallbackContext) -> None:  # noqa: ANN401
        """Send the result of the action."""
        ann_type, ann_metadata = parse_annotation(inspect.signature(self._func).return_annotation)

        if ann_type is pathlib.Path and isinstance(ann_metadata, Photo):
            await send_photo(result, caption=ann_metadata.caption, update=update, context=context)
        elif ann_type is pathlib.Path:
            await send_document(result, update=update, context=context)
        elif ann_type is str:
            await send_text(result, update=update, context=context)
        elif ann_type is None:
            self._logger.debug("Function returned None, skipping reply")
        else:
            msg = f"Unexpected return type {ann_type} from action '{self.name}'"
            raise TypeError(msg)

    async def __call__(self, update: Update, context: CallbackContext) -> None:
        """Execute the action."""
        if not self.is_valid():
            self._logger.warning("Not valid, skipping execution")
            return

        self._logger.debug("Executing")

        pos_args = []
        keyword_args = {}

        for name, param in inspect.signature(self._func).parameters.items():
            match name:
                case "update":
                    value = update
                case "context":
                    value = context
                case "logger":
                    value = self._logger
                case "user":
                    value = get_user_from_telegram_id(update.effective_user.id)
                case "return":
                    # Skip return annotation
                    continue
                case _:
                    value = None

            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                pos_args.append(value)
            else:
                keyword_args[name] = value

        result: Any = await self._func(*pos_args, **keyword_args)

        if self._validate_result(result):
            await self._send_result(result, update, context)

        self._logger.debug("Executed")
        raise ApplicationHandlerStop

    def __repr__(self) -> str:
        """Return a string representation of the Action object."""
        return f"Action '{self.name}' ({', '.join(f'/{cmd}' for cmd in self.commands)}) [-> {self._func.__name__}]"
