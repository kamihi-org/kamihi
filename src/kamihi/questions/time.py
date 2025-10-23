"""
Generic time reusable question.

License:
    MIT

"""

from datetime import time
from typing import Any

from telegram import Update
from telegram.ext import CallbackContext

from kamihi.base import get_settings

from .datetime import Datetime


class Time(Datetime):
    """Generic time reusable question."""

    error_text: str = get_settings().questions.time_error_text

    async def _validate_internal(
        self,
        response: Any,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Any:
        """
        Validate the response as a time.

        Args:
            response (str): The response to validate.
            update (Update | None): The update object. Defaults to None.
            context (CallbackContext | None): The callback context. Defaults to None.

        Returns:
            time: The validated time response.

        """
        dt = await super()._validate_internal(response)
        return dt.time()
