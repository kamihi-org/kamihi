"""
Generic string reusable question.

License:
    MIT

"""

from .question import Question


class String(Question):
    """Generic string reusable question."""

    def __init__(self, text: str) -> None:
        """
        Initialize an instance of the String question.

        Args:
            text (str): The text of the question.

        """
        super().__init__()
        self.question_text = text
