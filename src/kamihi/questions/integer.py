"""
Generic integer reusable question.

License:
    MIT

"""

from typing import Any

from kamihi.base import get_settings

from .question import Question


class Integer(Question):
    """Generic integer reusable question."""

    error_text: str = get_settings().questions.integer_error_text
    le: int | None = None
    ge: int | None = None
    lt: int | None = None
    gt: int | None = None
    multiple_of: int | None = None

    def __init__(
        self,
        text: str,
        error_text: str = None,
        le: int | None = None,
        ge: int | None = None,
        lt: int | None = None,
        gt: int | None = None,
        multiple_of: int | None = None,
    ) -> None:
        """
        Initialize an instance of the Integer question.

        Args:
            text (str): The text of the question.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a value from settings.
            le (int | None, optional): The maximum acceptable value (exclusive). Defaults to None.
            ge (int | None, optional): The minimum acceptable value (exclusive). Defaults to None
            lt (int | None, optional): The maximum acceptable value (inclusive). Defaults to None.
            gt (int | None, optional): The minimum acceptable value (inclusive). Defaults to None
            multiple_of (int | None, optional): The value must be a multiple of this number. Defaults to None.

        """
        super().__init__()
        self.question_text = text

        if error_text is not None:
            self.error_text = error_text

        self.le = le
        self.ge = ge
        self.lt = lt
        self.gt = gt
        self.multiple_of = multiple_of

    async def _validate_internal(self, response: Any) -> int:  # noqa: ANN401
        """
        Validate the response as an integer within the specified range.

        Args:
            response (Any): The response to validate.

        Returns:
            int: The validated integer response.

        Raises:
            ValueError: If the response is not a valid integer or out of range.

        """
        try:
            value = int(response)
        except ValueError as e:
            msg = "The provided response is not a valid integer."
            raise ValueError(msg) from e

        if self.le is not None and value > self.le:
            msg = f"The provided integer must be less than or equal to {self.le}."
            raise ValueError(msg)

        if self.ge is not None and value < self.ge:
            msg = f"The provided integer must be greater than or equal to {self.ge}."
            raise ValueError(msg)

        if self.lt is not None and value >= self.lt:
            msg = f"The provided integer must be less than {self.lt}."
            raise ValueError(msg)

        if self.gt is not None and value <= self.gt:
            msg = f"The provided integer must be greater than {self.gt}."
            raise ValueError(msg)

        if self.multiple_of is not None and value % self.multiple_of != 0:
            msg = f"The provided integer must be a multiple of {self.multiple_of}."
            raise ValueError(msg)

        return value

    async def validate_after(self, response: int) -> int:
        """
        Validate the integer response after Kamihi's built-in validation.

        Args:
            response (int): The response to validate.

        Returns:
            int: The further validated integer response.

        Raises:
            ValueError: If the response is invalid.

        """
        return response
