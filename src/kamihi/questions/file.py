"""
Generic file reusable question.

License:
    MIT

"""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal

from telegram import Document, Update
from telegram.constants import FileSizeLimit
from telegram.ext import CallbackContext, filters

from .question import Question


class File(Question):
    """Generic file reusable question."""

    return_as: Literal["path", "bytes"]
    max_size: int = int(FileSizeLimit.FILESIZE_DOWNLOAD)
    allowed_extensions: list[str] = []
    allowed_mime_types: list[str] = []

    error_text: str = "Please upload a valid file."

    def __init__(
        self,
        text: str,
        error_text: str = None,
        return_as: Literal["path", "bytes"] = "path",
        max_size: int = None,
        allowed_extensions: list[str] = None,
        allowed_mime_types: list[str] = None,
    ) -> None:
        """
        Initialize an instance of the File question.

        Args:
            text (str): The text of the question.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a preset message.
            return_as (Literal["path", "bytes"], optional): The format in which to return the file. Defaults to "path".
            max_size (int, optional): The maximum allowed file size in bytes. Defaults to FileSizeLimit.FILESIZE_DOWNLOAD.
            allowed_extensions (list[str], optional): List of allowed file extensions (without leading dot!). Defaults to an empty list.
            allowed_mime_types (list[str], optional): List of allowed MIME types. Defaults to an empty list.

        """
        super().__init__()
        self.question_text = text

        if error_text is not None:
            self.error_text = error_text

        if max_size is not None:
            self.max_size = max_size

        if allowed_extensions is not None:
            if any(ext.endswith(".") for ext in allowed_extensions):
                raise ValueError("File extensions must not end with a dot (e.g., use 'pdf' instead of 'pdf.').")
            self.allowed_extensions = list(set(allowed_extensions))

        if allowed_mime_types is not None:
            self.allowed_mime_types = list(set(allowed_mime_types))

        self.return_as = return_as

    @property
    def filters(self) -> filters.BaseFilter:
        """
        Return the filters for the answer to the file question.

        Returns:
            filters.BaseFilter: The filters to capture valid file responses.

        """
        return filters.ATTACHMENT

    async def get_response(self, update: Update, context: CallbackContext) -> Document:
        """
        Extract and validate the file from the user's response.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        Returns:
            Document: The Telegram Document object from the update.

        """
        return update.message.document

    def cast(self, path: Path) -> Path | bytes:
        """
        Convert the saved file path to the desired return type.

        Args:
            path (Path): The path to the saved file.

        Returns:
            ReturnT: The file in the desired return type (Path or bytes).

        """
        if self.return_as == "bytes":
            return path.read_bytes()
        return path

    async def _validate_internal(
        self,
        response: Document,
        update: Update | None = None,
        context: CallbackContext | None = None,
    ) -> Path | bytes:
        """
        Validate the response as a file and download it to a temporary local path.

        Args:
            response (Document): The response to validate.
            update (Update | None): The update object. Defaults to None.
            context (CallbackContext | None): The callback context. Defaults to None.

        Returns:
            Path: The path to the downloaded file.

        """
        if response.file_size > self.max_size:
            raise ValueError(self.error_text)

        file = await response.get_file()
        with NamedTemporaryFile(delete=False) as temp_file:
            await file.download_to_drive(custom_path=temp_file.name)
            return self.cast(Path(temp_file.name))
