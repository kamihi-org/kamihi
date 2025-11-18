"""
Action helper class.

License:
    MIT

"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Coroutine, Sequence
from inspect import Parameter
from pathlib import Path
from random import randint
from typing import Annotated, Any, get_args, get_origin

import loguru
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from telegram import Update
from telegram.constants import BotCommandLimit
from telegram.ext import BaseHandler, CallbackContext, CommandHandler, ConversationHandler

from kamihi.base import get_settings
from kamihi.base.utils import COMMAND_REGEX
from kamihi.datasources import DataSource
from kamihi.db import BaseUser, Job, RegisteredAction, get_engine
from kamihi.questions import Question
from kamihi.tg import send
from kamihi.tg.default_handlers import cancel
from kamihi.tg.handlers import AuthHandler
from kamihi.users import get_user_from_telegram_id, get_users_of_action


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

        self._save_to_db()

        self._logger.debug("Successfully registered")

    def _make_first_entry(
        self,
        base_state: int,
    ) -> Callable[[Update, CallbackContext], Coroutine[Any, Any, int]]:
        """
        Construct the entry function for the questions.

        Args:
            base_state (int): The current state of the conversation.

        Returns:
            Callable: The constructed entry function.

        """

        async def _entry(update: Update, context: CallbackContext) -> int:
            """Entry function for the questions."""
            self._logger.debug("Starting Q&A")
            context.chat_data["questions"] = {}

            return await self._questions[0].entry(base_state - 1)(update, context)

        return _entry

    def _make_last_entry(
        self, current_state: int, prev_exit: Callable[[Update, CallbackContext], Coroutine[Any, Any, bool]]
    ) -> Callable[[Update, CallbackContext], Coroutine[Any, Any, int]]:
        """
        Construct the exit function for the questions.

        Args:
            current_state (int): The current state of the conversation.
            prev_exit (Callable): The exit function of the previous question.

        Returns:
            Callable: The constructed exit function.

        """

        async def _entry(update: Update, context: CallbackContext) -> int:
            """Exit function for the questions."""
            exited_successfully = await prev_exit(update, context)
            if not exited_successfully:
                return current_state

            self._logger.debug("Finished Q&A")
            await self(update, context)
            context.chat_data.pop("questions", None)
            return ConversationHandler.END

        return _entry

    def _construct_questions_handler(self) -> ConversationHandler:
        """
        Construct the handler for the action when it has questions.

        Returns:
            AuthHandler: The constructed handler.

        """
        base_state = randint(1, 2**31 - 1)

        entry = AuthHandler(
            CommandHandler(self.commands, self._make_first_entry(base_state)),
            self.name,
        )

        states: dict[int, list[BaseHandler]] = {}

        for i, question in enumerate(self._questions):
            state_id = base_state + i

            if i == len(self._questions) - 1:
                handler = question.handler(self._make_last_entry(state_id, question.exit()))
            else:
                next_entry = self._questions[i + 1].entry(state_id, question.exit())
                handler = question.handler(next_entry)
            states[state_id] = [handler]

        return ConversationHandler(
            entry_points=[entry],
            states=states,
            fallbacks=[CommandHandler(get_settings().responses.cancel_command, cancel)],
            allow_reentry=True,
            conversation_timeout=get_settings().questions.timeout,
        )

    @property
    def handler(self) -> AuthHandler | ConversationHandler:
        """Construct a CommandHandler for the action."""
        if not self._questions:
            return AuthHandler(CommandHandler(self.commands, self.__call__), self.name)
        return self._construct_questions_handler()

    @property
    def jobs(self) -> list[tuple[Job, Callable[[CallbackContext], Coroutine[Any, Any, None]]]]:
        """Return a list of jobs associated with the action."""
        with Session(get_engine()) as session:
            sta = select(Job).where(Job.action.has(RegisteredAction.name == self.name))
            return [(job, self.run_scheduled) for job in session.execute(sta).scalars().all()]

    @property
    def users(self) -> Sequence[BaseUser]:
        """Return a list of telegram IDs of users authorized to use the action."""
        return get_users_of_action(self.name)

    @property
    def _parameters(self) -> dict[str, Parameter]:
        """Return a list of parameters that need to be filled."""
        return dict(inspect.signature(self._func).parameters)

    @property
    def _questions(self) -> list[Question]:
        """Return a list of parameters that need to be filled using questions."""
        return [
            get_args(param.annotation)[1].with_action(name, self._logger)
            for name, param in self._parameters.items()
            if get_origin(param.annotation) is Annotated and isinstance(get_args(param.annotation)[1], Question)
        ]

    @property
    def _message_templates(self) -> dict[str, Template]:
        """Return a dictionary of message templates associated with the action."""
        return {name: self._files.get_template(name) for name in self._files.list_templates(extensions=".md.jinja")}

    @property
    def _request_templates(self) -> dict[str, Template]:
        """Return a list of request templates associated with the action."""
        return {
            name: self._files.get_template(name)
            for name in self._files.list_templates(filter_func=lambda x: x.endswith((".sql", ".sql.jinja")))
        }

    @property
    def _folder_path(self) -> Path:
        """Return the folder path where the action is defined."""
        return Path(self._func.__code__.co_filename).parent

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
        if any(
            param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            for param in self._parameters.values()
        ):
            msg = "Function parameters '*args' and '**kwargs' are not supported"
            raise ValueError(msg)

    def _validate_requests(self) -> None:
        """Validate the SQL requests associated with the action."""
        datasource_names = set(self._datasources.keys())
        discarded_files = []
        for file in self._request_templates:
            ds_name = re.search(r"\.(.*?)\.", file)
            if ds_name is None:
                self._logger.warning(
                    "Request file does not specify a datasource, it will be ignored.",
                    file=file,
                )
                discarded_files.append(file)
                continue
            ds_name = ds_name.group(1)
            if ds_name not in datasource_names:
                self._logger.warning(
                    "Request file specifies an unknown datasource, it will be ignored.",
                    file=file,
                    ds_name=ds_name,
                )
                discarded_files.append(file)
                continue

        for file in discarded_files:
            self._request_templates.pop(file, None)

    def _save_to_db(self) -> None:
        """Save the action to the database."""
        with Session(get_engine()) as session:
            sta = select(RegisteredAction).where(RegisteredAction.name == self.name)
            existing_action = session.execute(sta).scalars().first()
            if existing_action:
                existing_action.description = self.description
                session.add(existing_action)
                self._logger.trace("Updated action in database")
            else:
                session.add(RegisteredAction(name=self.name, description=self.description))
                self._logger.trace("Added action to database")
            session.commit()

    def _params_dict(self, context: CallbackContext, update: Update = None) -> dict[str, Any]:
        return {
            "update": update if update else None,
            "context": context,
            "logger": self._logger,
            "user": (
                get_user_from_telegram_id(update.effective_user.id)
                if update
                else get_user_from_telegram_id(context.job.data.get("user"))
            ),
            "users": (
                get_users_of_action(self.name)
                if update
                else [get_user_from_telegram_id(tg_id) for tg_id in context.job.data.get("users", [])]
            ),
            "templates": self._message_templates,
            "action_folder": self._folder_path,
            **context.chat_data.get("questions", {}),
            **(context.job.data.get("args", {}) if context.job and context.job.data else {}),
        }

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

    async def _param_data(self, name: str, param: Parameter, context: dict) -> list:
        """Fill data for a specific parameter."""
        if get_origin(param.annotation) is Annotated:
            args = get_args(param.annotation)
            if len(args) == 2 and isinstance(args[1], str):
                req = args[1]
                if req not in self._request_templates:
                    msg = "Request file specified in annotation not found"
                    raise ValueError(msg)
            else:
                msg = "Invalid Annotated arguments"
                raise ValueError(msg)
        else:
            if name == "data" and len(self._request_templates) == 1:
                req = next(iter(self._request_templates.keys()))
            elif name == "data" and len(self._request_templates) > 1:
                raise ValueError("Multiple requests found, specify one using annotated pattern")
            elif name.startswith("data_"):
                name = name.replace("data_", "")
                req = [r for r in self._request_templates if r.startswith(f"{name}.")]
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
        if ds_name is None:
            raise ValueError("Cannot obtain datasource from request filename")
        return await self._datasources[ds_name.group(1)].fetch(self._request_templates[req].render(context))

    async def _fill_parameters(
        self, context: CallbackContext, update: Update = None
    ) -> tuple[list[Any], dict[str, Any]]:
        """Fill parameters for the action call."""
        parameters = self._params_dict(context, update)

        pos_args = []
        keyword_args = {}

        for name, param in sorted(
            self._parameters.items(), key=lambda x: 1 if x[0] == "data" or x[0].startswith("data_") else 0
        ):
            if name.startswith("template"):
                value = self._param_template(name, param)
            elif name == "data" or name.startswith("data_"):
                value = await self._param_data(name, param, parameters)
            else:
                value = parameters.get(name)

            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                pos_args.append(value)
            else:
                keyword_args[name] = value

        return pos_args, keyword_args

    async def __call__(self, update: Update, context: CallbackContext) -> int:
        """Execute the action."""
        self._logger.debug("Executing action")

        pos_args, keyword_args = await self._fill_parameters(context, update)

        result: Any = await self._func(*pos_args, **keyword_args)

        await send(result, update.effective_chat.id, context)

        self._logger.debug("Finished execution")
        return ConversationHandler.END

    async def run_scheduled(self, context: CallbackContext) -> None:
        """Execute the action in a job context."""
        per_user = context.job.data.get("per_user", False)

        self._logger.debug("Executing scheduled action", per_user=per_user)

        if per_user:
            for telegram_id in context.job.data.get("users", []):
                context.job.data["user"] = telegram_id
                pos_args, keyword_args = await self._fill_parameters(context)

                result: Any = await self._func(*pos_args, **keyword_args)

                await send(result, telegram_id, context)
        else:
            pos_args, keyword_args = await self._fill_parameters(context)

            result: Any = await self._func(*pos_args, **keyword_args)

            for telegram_id in context.job.data.get("users", []):
                await send(result, telegram_id, context)

            self._logger.debug("Finished scheduled execution")

    def __repr__(self) -> str:
        """Return a string representation of the Action object."""
        return f"Action '{self.name}' ({', '.join(f'/{cmd}' for cmd in self.commands)}) [-> {self._func.__name__}]"

    @classmethod
    def clean_up(cls, keep: list[str]) -> None:
        """Clean up the action from the database."""
        with Session(get_engine()) as session:
            statement = select(RegisteredAction).where(RegisteredAction.name.not_in(keep))
            actions = session.execute(statement).scalars().all()
            for action in actions:
                session.delete(action)
            session.commit()
