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
from telegram import Location as InputMediaLocation
from telegram.constants import LocationLimit
from telegramify_markdown import markdownify as md


@dataclass
class Media:
    """
    Represents a media type for the Kamihi bot.

    This is a base class for different media types like Photo and Document.

    Attributes:
        path (os.PathLike): Path to the media file.
        caption (str | None): Optional caption for the media.

    """

    path: str | Path | IO[bytes] | bytes
    caption: str | None = None
    filename: str | None = None

    def _get_filename(self) -> str | None:
        """
        Get the filename of the media.

        Returns:
            str | None: The filename if available, otherwise None.

        """
        if self.filename:
            return self.filename

        if isinstance(self.path, Path):
            return self.path.name

        return None


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
            media=self.path.read_bytes(),
            caption=md(self.caption) if self.caption else None,
            filename=self._get_filename(),
        )


@dataclass
class Photo(Media):
    """Represents a photo media type."""

    def as_input_media(self) -> InputMediaPhoto:
        """
        Convert the Photo to the InputMediaDocument class for sending.

        Returns:
            dict: A dictionary representation of the photo for input media.

        """
        return InputMediaPhoto(
            media=self.path.read_bytes(),
            caption=md(self.caption) if self.caption else None,
            filename=self._get_filename(),
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
            media=self.path.read_bytes(),
            caption=md(self.caption) if self.caption else None,
            filename=self._get_filename(),
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
            media=self.path.read_bytes(),
            caption=md(self.caption) if self.caption else None,
            filename=self._get_filename(),
            performer=self.performer,
            title=self.title,
        )


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
        if horizontal_accuracy and not (0.0 <= horizontal_accuracy <= float(LocationLimit.HORIZONTAL_ACCURACY)):
            msg = f"Horizontal accuracy must be between 0 and {LocationLimit.HORIZONTAL_ACCURACY}, got {horizontal_accuracy}"
            raise ValueError(msg)

        self.latitude = latitude
        self.longitude = longitude
        self.horizontal_accuracy = horizontal_accuracy

    def as_input_media(self) -> InputMediaLocation:
        """
        Convert the Location to the InputMediaLocation class for sending.

        Returns:
            InputMediaLocation: An instance of InputMediaLocation with the location data.

        """
        return InputMediaLocation(
            latitude=self.latitude,
            longitude=self.longitude,
            horizontal_accuracy=self.horizontal_accuracy,
        )
