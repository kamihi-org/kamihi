"""
Generic boolean reusable question.

License:
    MIT

"""

from typing import Any

from telegram import Update
from telegram.ext import CallbackContext

from kamihi.base import get_settings

from .question import Question


class Bool(Question):
    """Generic boolean reusable question."""

    error_text: str = get_settings().questions.bool_error_text
    true_values: set[str] = get_settings().questions.bool_true_values
    false_values: set[str] = get_settings().questions.bool_false_values

    def __init__(
        self, text: str, error_text: str = None, true_values: set[str] = None, false_values: set[str] = None
    ) -> None:
        """
        Initialize an instance of the Bool question.

        Args:
            text (str): The text of the question.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a value from settings.
            true_values (set[str], optional): A set of strings that represent true values. Defaults to a value from settings.
            false_values (set[str], optional): A set of strings that represent false values. Defaults to a value from settings.

        """
        super().__init__()
        self.question_text = text

        if error_text is not None:
            self.error_text = error_text

        if true_values is not None:
            self.true_values.update(true_values)

        if false_values is not None:
            self.false_values.update(false_values)

    async def _validate_internal(
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> bool:
        """
        Validate the response as a boolean.

        Args:
            response (Any): The response to validate.
            update (Update | None): The update object. Defaults to None.
            context (CallbackContext | None): The callback context. Defaults to None.

        Returns:
            bool: The validated boolean response.

        Raises:
            ValueError: If the response is not a valid boolean.

        """
        if isinstance(response, bool):
            return response

        if isinstance(response, str):
            response_lower = response.strip().lower()
            if response_lower in self.true_values:
                return True
            if response_lower in self.false_values:
                return False
            raise ValueError(self.error_text)

        raise ValueError(self.error_text)
