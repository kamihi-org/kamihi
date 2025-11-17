"""
Media types for the Kamihi bot.

License:
    MIT

"""

from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

from jinja2 import Template
from loguru import logger
from ptb_pagination import InlineKeyboardPaginator
from sqlalchemy import delete
from sqlalchemy.orm import Session
from telegram import InlineKeyboardMarkup, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo
from telegram.constants import FileSizeLimit, LocationLimit
from telegramify_markdown import markdownify as md

from kamihi.base import get_settings
from kamihi.db import Pages as DbPages
from kamihi.db import get_engine


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


class Pages:
    """
    Represents a paginated media type.

    Attributes:
        id (str): The ID of the Pages instance.

    """

    id: str

    def __init__(
        self,
        data: list,
        page_template: Template,
        items_per_page: int = 5,
        first_page_template: Template = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a Pages instance.

        Args:
            data (list): List of data items to be paginated.
            page_template (str): Template for rendering each page.
            items_per_page (int): Number of items per page.
            first_page_template (str | None): Optional template for the first page. This page will not get elements from the `data` list passed to it.
            **kwargs: Additional keyword arguments to be passed to the template rendering, including to the first page template if provided.

        """
        pages = [
            md(page_template.render(data=dl, **kwargs))
            for dl in [data[i : i + items_per_page] for i in range(0, len(data), items_per_page)]
        ]
        if first_page_template:
            first_page = md(first_page_template.render(**kwargs))
            pages.insert(0, first_page)

        with Session(get_engine()) as session:
            pages = DbPages(pages=pages)
            session.add(pages)
            session.commit()

            self.id = pages.id

    @staticmethod
    def from_id(pages_id: str) -> Pages:
        """
        Retrieve a Pages instance from the database by its ID.

        Args:
            pages_id (str): The ID of the Pages instance.

        Returns:
            Pages: The Pages instance.

        """
        pages = Pages.__new__(Pages)
        pages.id = pages_id
        return pages

    def _db_pages(self, session: Session) -> type[DbPages]:
        """Retrieve the DbPages instance from the database."""
        db_pages = session.get(DbPages, self.id)
        if not db_pages:
            msg = f"No Pages found with ID {self.id}"
            raise ValueError(msg)
        return db_pages

    def __len__(self) -> int:
        """
        Get the number of pages.

        Returns:
            int: The number of pages.

        """
        with Session(get_engine()) as session:
            return len(self._db_pages(session).pages)

    def get_page(self, page_number: int) -> tuple[str, InlineKeyboardMarkup]:
        """
        Retrieve a specific page by its number.

        Args:
            page_number (int): The page number to retrieve.

        Returns:
            str: The content of the specified page.

        """
        self.clean_up(get_settings().db.pages_expiration_days)

        with Session(get_engine()) as session:
            db_pages = self._db_pages(session)
            if 0 < page_number < len(self):
                msg = f"Page number {page_number} is out of range. Valid range is 0 to {len(self)}"
                raise ValueError(msg)

            return str(db_pages.pages[page_number]), InlineKeyboardPaginator(
                page_count=len(self),
                current_page=page_number + 1,
                data_pattern=self.id + "#{page}",
            ).markup

    @staticmethod
    def clean_up(expire_days: int) -> None:
        """
        Clean up old pages from the database.

        Args:
            expire_days (int): Number of days after which pages are considered expired.

        """
        with Session(get_engine()) as session:
            expire_cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=expire_days)
            stmt = delete(DbPages).where(DbPages.created_at < expire_cutoff)
            session.execute(stmt)
            session.commit()
            logger.trace("Cleaned up old pages")
