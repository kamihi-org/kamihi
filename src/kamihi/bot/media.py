"""
Media types for the Kamihi bot.

License:
    MIT

"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Media:
    """
    Represents a media type for the Kamihi bot.

    This is a base class for different media types like Photo and Document.

    Attributes:
        caption (str | None): Optional caption for the media.

    """

    path: Path | None = None
    caption: str | None = None


@dataclass
class Document(Media):
    """Represents a document media type."""


@dataclass
class Photo(Media):
    """Represents a photo media type."""
