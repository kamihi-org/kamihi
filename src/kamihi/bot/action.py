"""
Action helper class.

License:
    MIT

"""

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

    def _filter_valid_commands(self, commands: list[str]) -> list[str]:
        """Filter valid commands and log invalid ones."""
        min_len, max_len = BotCommandLimit.MIN_COMMAND, BotCommandLimit.MAX_COMMAND
        valid_commands = []

        for cmd in commands:
            if not COMMAND_REGEX.match(cmd):
                logger.warning(
                    f"Command '/{cmd}' for action '{self.name}' was discarded: "
                    f"must be {min_len}-{max_len} chars of lowercase letters, digits and underscores"
                )
                continue
            valid_commands.append(cmd)

        return valid_commands

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

        commands = self._filter_valid_commands(commands)

        self.commands = commands
        self.description = description
        self.func = func

    @property
    def handler(self) -> CommandHandler:
        """Construct a CommandHandler for the action."""
        return CommandHandler(self.commands, self.__call__)

    async def __call__(self, update: Update, context: CallbackContext) -> None:
        """Execute the action."""
        result = await self.func()
        await reply_text(update, context, result)

        raise ApplicationHandlerStop

    def __repr__(self) -> str:
        """Return a string representation of the Action object."""
        return f"Action '{self.name}' ({', '.join(f'/{cmd}' for cmd in self.commands)})"
