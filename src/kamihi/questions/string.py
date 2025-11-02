"""
Generic string reusable question.

License:
    MIT

"""

import re
from typing import Any

from telegram import Update
from telegram.ext import CallbackContext

from kamihi.base import get_settings

from .question import Question


class String(Question):
    """Generic string reusable question."""

    error_text: str = get_settings().questions.string_error_text

    pattern: str | None
    min_length: int | None
    max_length: int | None

    def __init__(
        self,
        text: str,
        error_text: str = None,
        pattern: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        """
        Initialize an instance of the String question.

        Args:
            text (str): The text of the question.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a value from settings.
            pattern (str | None, optional): A regex pattern that the response must match. Defaults to None.
            min_length (int | None, optional): The minimum length of the string. Defaults to None.
            max_length (int | None, optional): The maximum length of the string. Defaults to

        """
        super().__init__()
        self.question_text = text

        if error_text is not None:
            self.error_text = error_text

        self.pattern = pattern
        self.min_length = min_length
        self.max_length = max_length

    async def _validate_internal(
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the response as a string.

        Args:
            response (str): The response to validate.
            update (Update | None): The update object. Defaults to None.
            context (CallbackContext | None): The callback context. Defaults to None.

        Returns:
            str: The validated string response.

        Raises:
            ValueError: If the response does not match the pattern.

        """
        try:
            value = str(response)
        except ValueError as e:
            raise ValueError(self.error_text) from e

        if self.pattern is not None and not re.fullmatch(self.pattern, value):
            raise ValueError(self.error_text)

        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError(self.error_text)

        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError(self.error_text)

        return value
