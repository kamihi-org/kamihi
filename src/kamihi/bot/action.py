"""
Action helper class.

License:
    MIT

"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any, get_args, get_origin

import loguru
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from loguru import logger
from telegram import Update
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CallbackContext, CommandHandler

from kamihi.datasources import DataSource
from kamihi.tg import send
from kamihi.tg.handlers import AuthHandler
from kamihi.users import get_user_from_telegram_id

from .models import RegisteredAction
from .utils import COMMAND_REGEX


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

    _folder_path: Path
    _func: Callable
    _logger: loguru.Logger
    _db_object: RegisteredAction | None
    _files: Environment
    _datasources: dict[str, DataSource]

    _valid: bool = True

    def __init__(
        self, name: str, commands: list[str], description: str, func: Callable, datasources: dict[str, DataSource]
    ) -> None:
        """
        Initialize the Action class.

        Args:
            name (str): The name of the action.
            commands (list[str]): List of commands associated.
            description (str): Description of the action.
            func (Callable): The function to be executed when the action is called.
            datasources (dict[str, DataSource]): Dictionary of data sources available for the action.

        """
        self.name = name
        self.commands = commands
        self.description = description

        self._folder_path = Path(func.__code__.co_filename).parent
        self._func = func
        self._logger = logger.bind(action=self.name)
        self._datasources = datasources
        self._files = Environment(
            loader=FileSystemLoader(self._folder_path),
            autoescape=select_autoescape(default_for_string=False),
        )

        self._validate_commands()
        self._validate_function()
        self._validate_requests()

        if not self.is_valid():
            self._db_object = None
            self._logger.warning("Failed to register")
            return

        self._db_object = self.save_to_db()

        self._logger.debug("Successfully registered")

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
        if any(
            param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            for param in parameters.values()
        ):
            self._logger.warning(
                "Special arguments '*args' and '**kwargs' are not supported in action"
                " parameters, they will be ignored. Beware that this may cause issues."
            )
            self._valid = False

    def _validate_requests(self) -> None:
        """Validate the SQL requests associated with the action."""
        datasource_names = set(self._datasources.keys())
        discarded_files = []
        for file in self._requests:
            if not any(file.endswith(f".{ds_name}.sql") for ds_name in datasource_names):
                self._logger.warning(
                    "Request file does not match any datasource, it will be ignored.",
                    file=file,
                )
                discarded_files.append(file)

        for file in discarded_files:
            self._requests.pop(file, None)

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

    @property
    def _requests(self) -> dict[str, Template]:
        """Return a list of request templates associated with the action."""
        return {name: self._files.get_template(name) for name in self._files.list_templates(extensions=".sql")}

    @property
    def _message_templates(self) -> dict[str, Template]:
        """Return a dictionary of message templates associated with the action."""
        return {name: self._files.get_template(name) for name in self._files.list_templates(extensions=".md.jinja")}

    def _get_message_template(self, name: str) -> Template | None:
        """Get a specific template by name."""
        return self._message_templates.get(name)

    def _get_datasource_for_file(self, name: str) -> str | None:
        """Get the datasource name for a specific file."""
        match = re.search(r"\.(.*?)\.", name)
        if match:
            return match.group(1)
        return None

    # skipcq: PY-R1000
    async def __call__(self, update: Update, context: CallbackContext) -> None:  # noqa: C901
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
                case "templates":
                    value = self._message_templates
                case s if s.startswith("template"):
                    if get_origin(param.annotation) is Annotated:
                        args = get_args(param.annotation)
                        if len(args) == 2 and args[0] is Template and isinstance(args[1], str):
                            value = self._get_message_template(args[1])
                        else:
                            self._logger.warning(
                                "Invalid Annotated arguments for parameter '{name}'",
                                name=name,
                            )
                            value = None
                    else:
                        value = self._get_message_template(f"{self.name}.md.jinja")
                case s if s == "data" or s.startswith("data_"):
                    err = ""
                    if get_origin(param.annotation) is Annotated:
                        args = get_args(param.annotation)
                        if len(args) == 2 and isinstance(args[1], str):
                            req = args[1]
                        else:
                            err = "Invalid Annotated arguments"
                            req = None
                    else:
                        if name == "data" and len(self._requests) == 1:
                            req = next(iter(self._requests.keys()))
                        elif name == "data" and len(self._requests) > 1:
                            err = "Multiple possible requests found, please specify one using Annotated"
                            req = None
                        elif name.startswith("data_"):
                            req = [r for r in self._requests if r.startswith(f"{name.replace('data_', '')}.")]
                            if not req:
                                err = f"No request found for '{name}'"
                                req = None
                            elif len(req) > 1:
                                err = f"Multiple requests found for '{name}', please specify one using Annotated"
                                req = None
                            else:
                                req = req[0]
                        else:
                            err = f"No request found"
                            req = None

                    if err:
                        self._logger.warning(err, parameter=name)
                        value = None
                    else:
                        ds_name = self._get_datasource_for_file(req)
                        if ds_name and ds_name in self._datasources:
                            value = await self._datasources[ds_name].fetch(self._requests[req].render())
                        else:
                            self._logger.warning(
                                "No datasource found for request '{req}', it will be set to None",
                                req=req,
                            )
                            value = None
                case _:
                    self._logger.warning(
                        "Parameter '{name}' is not supported, it will be set to None",
                        name=name,
                    )
                    value = None

            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                pos_args.append(value)
            else:
                keyword_args[name] = value

        result: Any = await self._func(*pos_args, **keyword_args)

        await send(result, update, context)

        self._logger.debug("Finished execution")
        raise ApplicationHandlerStop

    def __repr__(self) -> str:
        """Return a string representation of the Action object."""
        return f"Action '{self.name}' ({', '.join(f'/{cmd}' for cmd in self.commands)}) [-> {self._func.__name__}]"
