"""
Generic date reusable question.

License:
    MIT

"""

from datetime import date
from typing import Any

from kamihi.base import get_settings

from .datetime import Datetime


class Date(Datetime):
    """Generic date reusable question."""

    error_text: str = get_settings().questions.date_error_text

    async def _validate_internal(self, response: Any) -> date:  # noqa: ANN401
        """
        Validate the response as a date.

        Args:
            response (str): The response to validate.

        Returns:
            date: The validated date response.

        """
        dt = await super()._validate_internal(response)
        return dt.date()
