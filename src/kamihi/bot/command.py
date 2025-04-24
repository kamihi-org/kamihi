"""
Command module for Kamihi bot.

License:
    MIT

"""

import re
from collections.abc import Callable, Coroutine

from loguru import logger
from telegram import Update
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CallbackContext, CommandHandler, ConversationHandler

from kamihi.tg.send import reply_text


class Command:
    """
    Command class for Kamihi bot.

    This class provides helpers for defining commands and their handlers.

    Attributes:
        name (str): The name of the command.
        commands (list[str]): List of commands associated.
        description (str): Description of the command.
        function (Coroutine): The function to be executed when the command is called.

    """

    name: str
    commands: list[str]
    description: str
    func: Callable
    _command_regex = re.compile(rf"^[a-z0-9_]{{{BotCommandLimit.MIN_COMMAND},{BotCommandLimit.MAX_COMMAND}}}$")

    def _filter_valid_commands(self, commands: list[str], callback_name: str) -> list[str]:
        """Filter valid commands and log invalid ones."""
        min_len, max_len = BotCommandLimit.MIN_COMMAND, BotCommandLimit.MAX_COMMAND
        valid_commands = []

        for cmd in commands:
            if not self._command_regex.match(cmd):
                logger.warning(
                    f"Command '{cmd}' for `{callback_name}` was discarded: "
                    f"must be {min_len}-{max_len} chars of lowercase letters, digits and underscores"
                )
                continue
            valid_commands.append(cmd)

        return valid_commands

    def __init__(self, name: str, commands: list[str], description: str, function: Callable) -> None:
        """
        Initialize the Command class.

        Args:
            name (str): The name of the command.
            commands (list[str]): List of commands associated.
            description (str): Description of the command.
            function (Callable): The function to be executed when the command is called.

        """
        commands = self._filter_valid_commands(commands, name)

        self.name = name
        self.commands = commands
        self.description = description
        self.func = function

    @property
    def handler(self) -> CommandHandler:
        """Construct a CommandHandler for the command."""
        return CommandHandler(self.commands, self.__call__)

    async def __call__(self, update: Update, context: CallbackContext) -> None:
        """Execute the command."""
        result = await self.func()
        await reply_text(update, context, result)

        raise ApplicationHandlerStop

    def __repr__(self) -> str:
        """Return a string representation of the Command object."""
        return f"Command `{self.name}` ({', '.join(f'/{cmd}' for cmd in self.commands)})"
