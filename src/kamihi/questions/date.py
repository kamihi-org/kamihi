"""
Generic date reusable question.

License:
    MIT

"""

from datetime import date, datetime
from typing import Any

from telegram import Update
from telegram.ext import CallbackContext

from kamihi.base import get_settings

from .datetime import Datetime


class Date(Datetime):
    """Generic date reusable question."""

    error_text: str = get_settings().questions.date_error_text

    before: date | None
    after: date | None
    in_the_past: bool
    in_the_future: bool

    def __init__(
        self,
        text: str,
        error_text: str = None,
        before: date | None = None,
        after: date | None = None,
        in_the_past: bool = False,  # noqa: FBT001, FBT002
        in_the_future: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """
        Initialize an instance of the Date question.

        Args:
            text (str): The text of the question.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a value from settings.
            before (date | None, optional): The latest acceptable date (exclusive). Defaults to None.
            after (date | None, optional): The earliest acceptable date (exclusive). Defaults to None
            in_the_past (bool, optional): Whether the date must be in the past. Defaults to False.
            in_the_future (bool, optional): Whether the date must be in the future. Defaults to False.

        """
        super().__init__(
            text=text,
            error_text=error_text,
            before=None if before is None else datetime.combine(before, datetime.min.time()),
            after=None if after is None else datetime.combine(after, datetime.min.time()),
            in_the_past=in_the_past,
            in_the_future=in_the_future,
        )

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
            date: The validated date response.

        """
        dt = await super()._validate_internal(response)
        return dt.date()
