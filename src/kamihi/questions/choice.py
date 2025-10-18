"""
Generic choice reusable question.

License:
    MIT

"""

from collections.abc import Callable, Coroutine, Iterable
from typing import Any, Literal

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler

from kamihi.base import get_settings
from kamihi.tg import send

from .question import Question


class Choice(Question):
    """Generic choice reusable question."""

    error_text: str = get_settings().questions.choice_error_text

    _choices: dict[str, Any] | Callable
    reply_type: Literal["simple", "keyboard", "inline"]

    def __init__(
        self,
        text: str,
        choices: dict[str, Any] | Iterable[str | tuple[str, Any]] | Callable,
        error_text: str = None,
        reply_type: Literal["simple", "keyboard", "inline"] = "simple",
    ) -> None:
        """
        Initialize an instance of a multiple-choice question.

        Args:
            text (str): The text of the question.
            choices (dict[str, Any] | Iterable[str | tuple[str, Any]]): The available choices for the question. Can be one of:
                - A dictionary mapping display text to return values.
                - An iterable of strings (where each string is both the display text and return value).
                - An iterable of tuples (where each tuple contains display text and return value).
                - A callable that returns one of the above.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a value from settings.
            reply_type (Literal["simple", "keyboard", "inline"], optional): The type of choice question. Defaults to "simple".

        """
        super().__init__()
        self.question_text = text

        if error_text is not None:
            self.error_text = error_text

        if isinstance(choices, dict) or callable(choices):
            self._choices = choices
        else:
            self._choices = {}
            for choice in choices:
                if isinstance(choice, tuple):
                    display_text, return_value = choice
                    self._choices[display_text] = return_value
                else:
                    self._choices[choice] = choice

        self.reply_type = reply_type

    @property
    def choices(self) -> dict[str, Any]:
        """Get the available choices for the question."""
        if callable(self._choices):
            result = self._choices()
            if isinstance(result, dict):
                return result
            choices_dict = {}
            for choice in result:
                if isinstance(choice, tuple):
                    display_text, return_value = choice
                    choices_dict[display_text] = return_value
                else:
                    choices_dict[choice] = choice
            return choices_dict
        return self._choices

    async def ask_question(self, update: Update, context: CallbackContext) -> None:
        """
        Ask the choice question to the user.

        Override this method to customize how the question is asked based on the reply type.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        """
        reply_markup = None
        match self.reply_type:
            case "keyboard":
                keyboard = [[choice] for choice in self.choices]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            case "inline":
                keyboard = [
                    [InlineKeyboardButton(choice, callback_data=self._param_name + "_" + choice)]
                    for choice in self.choices
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

    async def get_response(self, update: Update, context: CallbackContext) -> Any:  # noqa: ANN401
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
                msg = await send("Removing keyboard...", update, context, reply_markup=ReplyKeyboardRemove())
                await msg.delete()
                return update.message.text
            case "inline":
                await context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
                return update.callback_query.data.removeprefix(self._param_name + "_")

    async def _validate_internal(self, response: Any) -> Any:  # noqa: ANN401
        """
        Validate the response as a choice.

        Args:
            response (str): The response to validate.

        Returns:
            str: The validated choice response.

        """
        try:
            response_str = str(response).strip()
        except ValueError as e:
            raise ValueError(self.error_text) from e

        if response_str not in self.choices:
            raise ValueError(self.error_text)
        return self.choices[response_str]
