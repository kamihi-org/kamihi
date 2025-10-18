"""
Generic dynamic choice reusable question.

License:
    MIT

"""

from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, Literal

from telegram import Update
from telegram.ext import CallbackContext

from kamihi.datasources import DataSource

from .choice import Choice


class DynamicChoice(Choice):
    """Generic dynamic choice reusable question."""

    request: str | Path

    def __init__(
        self,
        text: str,
        request: str | Path,
        error_text: str = None,
        reply_type: Literal["simple", "keyboard", "inline"] = "simple",
    ) -> None:
        """
        Initialize an instance of a multiple-choice question.

        Args:
            text (str): The text of the question.
            request (str | Path): The name of the request file from which the choices will be obtained.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a value from settings.
            reply_type (Literal["simple", "keyboard", "inline"], optional): The type of choice question. Defaults to "simple".

        """
        super().__init__(text, {}, error_text, reply_type)
        self.request = request if isinstance(request, Path) else Path(request)

    async def get_choices(self, context: CallbackContext) -> dict[str, Any]:
        """
        Get the available choices for the question.

        Args:
            context (CallbackContext): The callback context.

        Returns:
            dict[str, Any]: The available choices as a dictionary mapping display text to return values.

        """
        datasources: dict[str, DataSource] = context.bot_data.get("datasources", {})
        ds = datasources[self.request.stem.split(".")[-1]]
        res = await ds.fetch(self.request)
        choices = {}
        for row in res:
            if len(row) >= 2:
                choices[str(row[0]).strip()] = row[1]
            elif len(row) == 1:
                choices[str(row[0]).strip()] = row[0]
        return choices

    async def ask_question(self, update: Update, context: CallbackContext) -> None:
        """
        Ask the choice question to the user.

        Override this method to customize how the question is asked based on the reply type.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        """
        self._choices = await self.get_choices(context)
        await super().ask_question(update, context)

    def exit(self) -> Callable[[Update, CallbackContext], Coroutine[Any, Any, bool]]:
        """
        Return the exit function for the question.

        Returns:
            Callable: The exit function for the question.

        """
        super_exit = super().exit()

        async def _exit(update: Update, context: CallbackContext) -> bool:
            """Exit function for the question."""
            result = await super_exit(update, context)
            if result:
                self._choices = None
            return result

        return _exit
