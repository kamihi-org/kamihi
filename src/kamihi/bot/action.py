"""
Action helper class.

License:
    MIT

"""

import inspect
from collections.abc import Callable

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

        self._validate_commands()
        self._validate_function()

        if self.is_valid():
            logger.debug(f"Successfully registered {self}")
        else:
            logger.warning(f"Failed to register {self}")

    def _validate_commands(self) -> None:
        """Filter valid commands and log invalid ones."""
        min_len, max_len = BotCommandLimit.MIN_COMMAND, BotCommandLimit.MAX_COMMAND

        # Remove duplicate commands
        self.commands = list(set(self.commands))

        # Filter out invalid commands
        for cmd in self.commands.copy():
            if not COMMAND_REGEX.match(cmd):
                logger.warning(
                    f"Command '/{cmd}' for action '{self.name}' was discarded: "
                    f"must be {min_len}-{max_len} chars of lowercase letters, digits and underscores"
                )
                self.commands.remove(cmd)

        # Mark as invalid if no commands are left
        if not self.commands:
            logger.warning(f"Action '{self.name}' has no valid commands")
            self._valid = False

    def _validate_function(self) -> None:
        """Validate the function passed."""
        # Check if the function is a coroutine
        if not inspect.iscoroutinefunction(self.func):
            logger.warning(
                f"Action '{self.name}' should be a coroutine, define it with 'async def {self.func.__name__}()' "
                f"instead of 'def {self.func.__name__}()'."
            )
            self._valid = False

    @property
    def handler(self) -> CommandHandler:
        """Construct a CommandHandler for the action."""
        return CommandHandler(self.commands, self.__call__)

    def is_valid(self) -> bool:
        """Check if the action is valid."""
        return self._valid

    async def __call__(self, update: Update, context: CallbackContext) -> None:
        """Execute the action."""
        parameters = inspect.signature(self.func).parameters
        pos_args = []
        keyword_args = {}

        for name, param in parameters.items():
            value = None
            match name:
                case "update":
                    value = update
                case "context":
                    value = context
                case _:
                    logger.warning(f"Unknown parameter '{name}', it will be set to None")

            match param.kind:
                case inspect.Parameter.POSITIONAL_OR_KEYWORD | inspect.Parameter.KEYWORD_ONLY:
                    keyword_args[name] = value
                case inspect.Parameter.POSITIONAL_ONLY:
                    pos_args.append(value)
                case inspect.Parameter.VAR_POSITIONAL | inspect.Parameter.VAR_KEYWORD:
                    logger.warning(
                        f"Special arguments '*args' and '**kwargs' are not supported in action"
                        f" parameters, they will be ignored. Beware that this may cause issues."
                    )

        result = await self.func()
        await reply_text(update, context, result)

        raise ApplicationHandlerStop

    def __repr__(self) -> str:
        """Return a string representation of the Action object."""
        return f"Action '{self.name}' ({', '.join(f'/{cmd}' for cmd in self.commands)}) [-> {self.func.__name__}]"
