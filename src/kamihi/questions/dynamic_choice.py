"""
Generic dynamic choice reusable question.

License:
    MIT

"""

from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, Literal

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler

from kamihi.base import get_settings
from kamihi.datasources import DataSource
from kamihi.tg import send

from .question import Question


class DynamicChoice(Question):
    """Generic dynamic choice reusable question."""

    error_text: str = get_settings().questions.dynamic_choice_error_text

    request: str | Path
    reply_type: Literal["simple", "keyboard", "inline"]

    def __init__(
        self,
        text: str,
        request: str | Path = None,
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
        super().__init__()
        self.question_text = text

        if error_text is not None:
            self.error_text = error_text

        if not self.request and request:
            self.request = request if isinstance(request, Path) else Path(request)
        elif not self.request:
            raise ValueError("A request file must be provided for DynamicChoice questions.")

        if not self.request.is_absolute():
            self.request = Path.cwd() / "questions" / self.request

        self.reply_type = reply_type

    async def get_choices(self, context: CallbackContext) -> dict[str, Any]:
        """
        Get the available choices for the question and save them in chat_data.

        Args:
            context (CallbackContext): The callback context.

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

        context.chat_data["questions"][self._param_name] = choices
        return choices

    async def ask_question(self, update: Update, context: CallbackContext) -> None:
        """
        Ask the choice question to the user, fetching dynamic choices.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        """
        choices = await self.get_choices(context)

        reply_markup = None
        match self.reply_type:
            case "keyboard":
                keyboard = [[choice] for choice in choices]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            case "inline":
                keyboard = [
                    [InlineKeyboardButton(choice, callback_data=self._param_name + "_" + choice)] for choice in choices
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
        await send(self.question_text, update, context, reply_markup)

    def handler(
        self, func: Callable[[Update, CallbackContext], Coroutine[Any, Any, Any]]
    ) -> MessageHandler | CallbackQueryHandler:
        """
        Return the handler for the answer to the question.

        Do not override this method. Instead, override the `filters` property to customize the filters used.

        Args:
            func (Callable): The function to handle the user's response.

        Returns:
            MessageHandler: The handler for the answer to the question.

        """
        if self.reply_type == "inline":
            return CallbackQueryHandler(func, pattern=rf"^{self._param_name}_")
        return MessageHandler(self.filters, func)

    async def get_response(self, update: Update, context: CallbackContext) -> Any:
        """
        Get the response from the user.

        Override this method to customize how the response is retrieved from the update and/or context.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        Returns:
            Any: The response from the user, which can be of any type.

        """
        match self.reply_type:
            case "simple":
                return update.message.text
            case "keyboard":
                msg = await send(
                    get_settings().questions.remove_keyboard_text, update, context, reply_markup=ReplyKeyboardRemove()
                )
                await msg.delete()
                return update.message.text
            case "inline":
                await context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
                return update.callback_query.data.removeprefix(self._param_name + "_")

    async def _validate_internal(
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the response as a choice.

        Args:
            response (str): The response to validate.
            update (Update | None): The update object. Optional.
            context (CallbackContext | None): The callback context.

        Returns:
            str: The validated choice response.

        """
        try:
            response_str = str(response).strip()
        except ValueError as e:
            raise ValueError(self.error_text) from e

        if not context:
            raise ValueError("Context is required for validating DynamicChoice responses.")

        choices = context.chat_data["questions"][self._param_name]

        if response_str not in choices:
            raise ValueError(self.error_text)
        return choices[response_str]
