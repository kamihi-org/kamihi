"""
Media types for the Kamihi bot.

License:
    MIT

"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import IO

from telegram import InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo
from telegram.constants import FileSizeLimit, LocationLimit
from telegramify_markdown import markdownify as md


@dataclass
class Media:
    """
    Represents a media type for the Kamihi bot.

    This is a base class for different media types like Photo and Document.

    Attributes:
        file (str | Path | IO[bytes] | bytes): The path to the media file or the file-like object.
        caption (str | None): Optional caption for the media.

    """

    file: str | Path | IO[bytes] | bytes
    caption: str | None = None
    filename: str | None = None

    _size_limit: float = float(FileSizeLimit.FILESIZE_UPLOAD)

    def __post_init__(self) -> None:
        """Post-initialization to ensure the media is valid."""
        if isinstance(self.file, str):
            self.file = Path(self.file)

        if isinstance(self.file, Path):
            # Add filename
            if not self.filename:
                self.filename = self.file.name

            # Validate file exists
            if not self.file.exists():
                mes = f"File {self.file} does not exist"
                raise ValueError(mes)

            # Validate it's a file, not a directory
            if not self.file.is_file():
                mes = f"Path {self.file} is not a file"
                raise ValueError(mes)

            # Check read permissions
            if not os.access(self.file, os.R_OK):
                mes = f"File {self.file} is not readable"
                raise ValueError(mes)

            # Check file size limit
            if self.file.stat().st_size > self._size_limit:
                mes = f"File {self.file} exceeds the size limit of {self._size_limit} bytes"
                raise ValueError(mes)
        elif isinstance(self.file, bytes):
            # Check file size limit
            if len(self.file) > self._size_limit:
                mes = f"Byte data exceeds the size limit of {self._size_limit} bytes"
                raise ValueError(mes)


@dataclass
class Document(Media):
    """Represents a document media type."""

    def as_input_media(self) -> InputMediaDocument:
        """
        Convert the Document to the InputMediaDocument class for sending.

        Returns:
            dict: A dictionary representation of the document for input media.

        """
        return InputMediaDocument(
            media=self.file.read_bytes() if isinstance(self.file, Path) else self.file,
            caption=md(self.caption) if self.caption else None,
            filename=self.filename,
        )


@dataclass
class Photo(Media):
    """Represents a photo media type."""

    def __post_init__(self) -> None:
        """Post-initialization to ensure the photo is valid with photo-specific size limit."""
        # Set the correct size limit before calling parent's __post_init__
        self._size_limit = float(FileSizeLimit.PHOTOSIZE_UPLOAD)
        super().__post_init__()

    def as_input_media(self) -> InputMediaPhoto:
        """
        Convert the Photo to the InputMediaDocument class for sending.

        Returns:
            dict: A dictionary representation of the photo for input media.

        """
        return InputMediaPhoto(
            media=self.file.read_bytes() if isinstance(self.file, Path) else self.file,
            caption=md(self.caption) if self.caption else None,
            filename=self.filename,
        )


@dataclass
class Video(Media):
    """Represents a video media type."""

    def as_input_media(self) -> InputMediaVideo:
        """
        Convert the Video to the InputMediaDocument class for sending.

        Returns:
            dict: A dictionary representation of the video for input media.

        """
        return InputMediaVideo(
            media=self.file.read_bytes() if isinstance(self.file, Path) else self.file,
            caption=md(self.caption) if self.caption else None,
            filename=self.filename,
        )


@dataclass
class Audio(Media):
    """Represents an audio media type."""

    performer: str | None = None
    title: str | None = None

    def as_input_media(self) -> InputMediaAudio:
        """
        Convert the Audio to the InputMediaDocument class for sending.

        Returns:
            dict: A dictionary representation of the audio for input media.

        """
        return InputMediaAudio(
            media=self.file.read_bytes() if isinstance(self.file, Path) else self.file,
            caption=md(self.caption) if self.caption else None,
            filename=self.filename,
            performer=self.performer,
            title=self.title,
        )


@dataclass
class Voice(Media):
    """Represents a voice media type."""

    def __post_init__(self) -> None:
        """Post-initialization to ensure the voice is valid with voice-specific size limit."""
        # Set the correct size limit before calling parent's __post_init__
        self._size_limit = float(FileSizeLimit.VOICE_NOTE_FILE_SIZE)
        super().__post_init__()


class Location:
    """
    Represents a location media type.

    Attributes:
        latitude (float): Latitude of the location, must be between -90 and 90.
        longitude (float): Longitude of the location, must be between -180 and 180.
        horizontal_accuracy (float | None): Optional horizontal accuracy in meters.

    """

    def __init__(self, latitude: float, longitude: float, horizontal_accuracy: float | None = None) -> None:
        """
        Initialize a Location instance with validated coordinates.

        Args:
            latitude (float): Latitude of the location (-90 to 90).
            longitude (float): Longitude of the location (-180 to 180).
            horizontal_accuracy (float | None): Optional horizontal accuracy in meters.


        Raises:
            ValueError: If latitude or longitude values are out of valid range.

        """
        if not -90 <= latitude <= 90:
            msg = f"Latitude must be between -90 and 90, got {latitude}"
            raise ValueError(msg)
        if not -180 <= longitude <= 180:
            msg = f"Longitude must be between -180 and 180, got {longitude}"
            raise ValueError(msg)
        if horizontal_accuracy and not 0.0 <= horizontal_accuracy <= float(LocationLimit.HORIZONTAL_ACCURACY):
            msg = (
                f"Horizontal accuracy must be between 0 "
                f"and {LocationLimit.HORIZONTAL_ACCURACY}, got {horizontal_accuracy}"
            )
            raise ValueError(msg)

        self.latitude = latitude
        self.longitude = longitude
        self.horizontal_accuracy = horizontal_accuracy
