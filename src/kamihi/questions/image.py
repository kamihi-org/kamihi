"""
Generic image reusable question.

License:
    MIT

"""

from pathlib import Path
from typing import Literal

from PIL import Image as PILImage
from telegram import PhotoSize, Update
from telegram.ext import CallbackContext, filters

from .file import File


class Image(File):
    """Generic image reusable question."""

    return_as: Literal["path", "bytes", "pil"]

    def __init__(
        self,
        text: str,
        error_text: str = "Please upload a valid image.",
        return_as: Literal["path", "bytes", "pil"] = "path",
        max_size: int = None,
        allowed_extensions: list[str] = None,
        allowed_mime_types: list[str] = None,
    ) -> None:
        """
        Initialize an instance of the Image question.

        Args:
            text (str): The text of the question.
            error_text (str, optional): The error text to display for invalid responses. Defaults to a preset message.
            return_as (Literal["path", "bytes", "pil"], optional): The format in which to return the image. Defaults to "path".
            max_size (int, optional): The maximum allowed file size in bytes. Defaults to FileSizeLimit.FILESIZE_DOWNLOAD.
            allowed_extensions (list[str], optional): List of allowed file extensions (without leading dot!). Defaults to common image formats.
            allowed_mime_types (list[str], optional): List of allowed MIME types. Defaults to common image MIME types.

        """
        super().__init__(
            text,
            error_text=error_text,
            return_as="path",
            max_size=max_size,
            allowed_extensions=allowed_extensions,
            allowed_mime_types=allowed_mime_types,
        )
        self.return_as = return_as

    @property
    def filters(self) -> filters.BaseFilter:
        """Return the filters for the answer to the image question."""
        return filters.PHOTO

    async def get_response(self, update: Update, context: CallbackContext) -> PhotoSize:
        """
        Extract and validate the file from the user's response.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.

        Returns:
            Document: The Telegram Document object from the update.

        """
        return update.message.photo[-1]

    def cast(self, path: Path) -> Path | bytes | PILImage.Image:
        """
        Convert the saved file path to the desired return type.

        Args:
            path (Path): The path to the saved file.

        Returns:
            ReturnT: The file in the desired return type (Path or bytes).

        """
        if self.return_as == "bytes":
            return path.read_bytes()
        if self.return_as == "pil":
            return PILImage.open(path)
        return path
