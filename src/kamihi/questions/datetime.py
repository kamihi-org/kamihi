"""
Generic datetime reusable question.

License:
    MIT

"""

from datetime import datetime
from typing import Any

import dateparser
from telegram import Update
from telegram.ext import CallbackContext

from kamihi.base import get_settings

from .question import Question


class Datetime(Question):
    """Generic date reusable question."""

    error_text: str = get_settings().questions.datetime_error_text

    before: datetime | None
    after: datetime | None
    in_the_past: bool
    in_the_future: bool

    def __init__(
        self,
        text: str,
        error_text: str = None,
        before: datetime | None = None,
        after: datetime | None = None,
        in_the_past: bool = False,  # noqa: FBT001, FBT002
        in_the_future: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """
        Initialize an instance of the Datetime question.

        Args:
            text (str): The text of the question.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a value from settings.
            before (datetime | None, optional): The latest acceptable date (exclusive). Defaults to None.
            after (datetime | None, optional): The earliest acceptable date (exclusive). Defaults to None
            in_the_past (bool, optional): Whether the date must be in the past. Defaults to False.
            in_the_future (bool, optional): Whether the date must be in the future. Defaults to False.

        """
        super().__init__()
        self.question_text = text

        if error_text is not None:
            self.error_text = error_text

        self.before = before
        self.after = after
        self.in_the_past = in_the_past
        self.in_the_future = in_the_future

    async def _validate_internal(
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the response as a date.

        Args:
            response (str): The response to validate.
            update (Update | None): The update object. Defaults to None.
            context (CallbackContext | None): The callback context. Defaults to None.

        Returns:
            str: The validated date response.

        Raises:
            ValueError: If the response is not a valid date.

        """
        try:
            dt = dateparser.parse(response)
        except ValueError as e:
            raise ValueError(self.error_text) from e

        if datetime is None:
            raise ValueError(self.error_text)

        if self.before is not None and dt >= self.before:
            raise ValueError(self.error_text)

        if self.after is not None and dt <= self.after:
            raise ValueError(self.error_text)

        if self.in_the_past and dt >= datetime.now(get_settings().timezone_obj):
            raise ValueError(self.error_text)

        if self.in_the_future and dt <= datetime.now(get_settings().timezone_obj):
            raise ValueError(self.error_text)

        return dt
