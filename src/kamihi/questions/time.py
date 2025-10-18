"""
Generic time reusable question.

License:
    MIT

"""

from datetime import time
from typing import Any

from kamihi.base import get_settings

from .datetime import Datetime


class Time(Datetime):
    """Generic time reusable question."""

    error_text: str = get_settings().questions.time_error_text

    async def _validate_internal(self, response: Any) -> time:  # noqa: ANN401
        """
        Validate the response as a time.

        Args:
            response (str): The response to validate.

        Returns:
            time: The validated time response.

        """
        dt = await super()._validate_internal(response)
        return dt.time()
