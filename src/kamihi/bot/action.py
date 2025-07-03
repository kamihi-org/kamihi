"""
Action helper class.

License:
    MIT

"""

from __future__ import annotations

import inspect
import pathlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import loguru
from loguru import logger
from telegram import Message, Update
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CallbackContext, CommandHandler
from typeguard import TypeCheckError, check_type

from kamihi.bot.media import Audio, Document, Location, Photo, Video
from kamihi.tg import send_document, send_text
from kamihi.tg.handlers import AuthHandler
from kamihi.tg.send import send_audio, send_location, send_photo, send_video
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
        ann = inspect.signature(self._func).return_annotation
        if ann is not inspect.Signature.empty:
            check_type(result, ann)
        return True

    async def _send_result(  # noqa: C901
        self,
        result: Any,  # noqa: ANN401
        update: Update,
        context: CallbackContext,
    ) -> Message | list[Message] | None:
        """Send the result of the action."""
        ann_type, ann_metadata = parse_annotation(inspect.signature(self._func).return_annotation)

        if isinstance(result, (list, tuple)):
            return [await self._send_result(item, update, context) for item in result]

        if isinstance(result, Location):
            return await send_location(result, update, context)

        if isinstance(result, Audio):
            return await send_audio(result.path, update, context, caption=result.caption)

        if isinstance(result, Video):
            return await send_video(result.path, update, context, caption=result.caption)

        if isinstance(result, Photo):
            return await send_photo(result.path, update, context, caption=result.caption)

        if isinstance(result, Document):
            return await send_document(result.path, update, context, caption=result.caption)

        if isinstance(result, Path):
            if ann_type is pathlib.Path and isinstance(ann_metadata, Document):
                return await send_document(result, update, context, caption=ann_metadata.caption)
            if ann_type is pathlib.Path and isinstance(ann_metadata, Photo):
                return await send_photo(result, update, context, caption=ann_metadata.caption)
            if ann_type is pathlib.Path and isinstance(ann_metadata, Video):
                return await send_video(result, update, context, caption=ann_metadata.caption)
            if ann_type is pathlib.Path and isinstance(ann_metadata, Audio):
                return await send_audio(result, update, context, caption=ann_metadata.caption)
            return await send_document(result, update, context)

        if isinstance(result, str):
            return await send_text(result, update, context)

        if result is None:
            self._logger.debug("Function returned None, skipping reply")
            return None

        msg = f"Unexpected return type {type(result)}"
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
