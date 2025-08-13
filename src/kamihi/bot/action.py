"""
Action helper class.

License:
    MIT

"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable
from inspect import Parameter
from pathlib import Path
from typing import Annotated, Any, get_args, get_origin

import loguru
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from loguru import logger
from telegram import Update
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CallbackContext, CommandHandler

from kamihi.base.utils import COMMAND_REGEX
from kamihi.datasources import DataSource
from kamihi.tg import send
from kamihi.tg.handlers import AuthHandler
from kamihi.users import get_user_from_telegram_id

from .models import RegisteredAction


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

    def __init__(
        self,
        name: str,
        commands: list[str],
        description: str,
        func: Callable,
        datasources: dict[str, DataSource] = None,
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

        self._datasources = datasources or {}

        self._files = Environment(
            loader=FileSystemLoader(self._folder_path),
            autoescape=select_autoescape(default_for_string=False),
        )

        self._validate_commands()
        self._validate_function()
        self._validate_requests()

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
                    "Command '{cmd}' was discarded: "
                    "must be {min_len}-{max_len} chars of lowercase letters, digits and underscores",
                    cmd=cmd,
                    min_len=int(min_len),
                    max_len=int(max_len),
                )
                self.commands.remove(cmd)

        # Mark as invalid if no commands are left
        if not self.commands:
            raise ValueError("No valid commands were given")

    def _validate_function(self) -> None:
        """Validate the function passed."""
        # Check if the function is a coroutine
        if not inspect.iscoroutinefunction(self._func):
            msg = (
                f"Function should be a coroutine, "
                f"define it with 'async def {self.name}()' instead of 'def {self.name}()'."
            )
            raise ValueError(msg)

        # Check if the function has valid parameters
        parameters = inspect.signature(self._func).parameters
        if any(
            param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            for param in parameters.values()
        ):
            msg = "Function parameters '*args' and '**kwargs' are not supported"
            raise ValueError(msg)

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
        return AuthHandler(CommandHandler(self.commands, self.__call__), self.name)

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

    def _param_template(self, _: str, param: Parameter) -> Template:
        """Get a template for a specific parameter."""
        if get_origin(param.annotation) is Annotated:
            args = get_args(param.annotation)
            if len(args) == 2 and args[0] is Template and isinstance(args[1], str):
                res = self._message_templates.get(args[1])
            else:
                msg = "Invalid Annotated arguments"
                raise ValueError(msg)
        else:
            res = self._message_templates.get(f"{self.name}.md.jinja")

        if res:
            return res

        msg = "No template found"
        raise ValueError(msg)

    async def _param_data(self, name: str, param: Parameter) -> list:
        """Fill data for a specific parameter."""
        if get_origin(param.annotation) is Annotated:
            args = get_args(param.annotation)
            if len(args) == 2 and isinstance(args[1], str):
                req = args[1]
                if req not in self._requests:
                    msg = "Request file specified in annotation not found"
                    raise ValueError(msg)
            else:
                msg = "Invalid Annotated arguments"
                raise ValueError(msg)
        else:
            if name == "data" and len(self._requests) == 1:
                req = next(iter(self._requests.keys()))
            elif name == "data" and len(self._requests) > 1:
                raise ValueError("Multiple requests found, specify one using annotated pattern")
            elif name.startswith("data_"):
                name = name.replace("data_", "")
                req = [r for r in self._requests if r.startswith(f"{name}.")]
                if not req:
                    msg = f"No request found matching '{name}'"
                    raise ValueError(msg)

                if len(req) > 1:
                    msg = f"Multiple requests matching '{name}' found, specify one using annotated pattern"
                    raise ValueError(msg)

                req = req[0]
            else:
                msg = "Default request not found"
                raise ValueError(msg)

        ds_name = re.search(r"\.(.*?)\.", req)
        return await self._datasources[ds_name.group(1)].fetch(self._requests[req].render())

    async def _fill_parameters(self, update: Update, context: CallbackContext) -> tuple[list[Any], dict[str, Any]]:
        """Fill parameters for the action call."""
        pos_args = []
        keyword_args = {}

        for name, param in inspect.signature(self._func).parameters.items():
            value: Any = None
            with self._logger.bind(param=name).catch(
                ValueError, level="WARNING", message="Failed to fill parameter, it will be set to None"
            ):
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
                        value = self._param_template(name, param)
                    case s if s == "data" or s.startswith("data_"):
                        value = await self._param_data(name, param)
                    case _:
                        msg = "Parameter is not supported"
                        raise ValueError(msg)

            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                pos_args.append(value)
            else:
                keyword_args[name] = value

        return pos_args, keyword_args

    async def __call__(self, update: Update, context: CallbackContext) -> None:
        """Execute the action."""
        self._logger.debug("Executing")

        pos_args, keyword_args = await self._fill_parameters(update, context)

        result: Any = await self._func(*pos_args, **keyword_args)

        await send(result, update, context)

        self._logger.debug("Finished execution")
        raise ApplicationHandlerStop

    def __repr__(self) -> str:
        """Return a string representation of the Action object."""
        return f"Action '{self.name}' ({', '.join(f'/{cmd}' for cmd in self.commands)}) [-> {self._func.__name__}]"
