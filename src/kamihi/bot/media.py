"""
Media types for the Kamihi bot.

License:
    MIT

"""

from dataclasses import dataclass


@dataclass
class Photo:
    """
    Represents a photo media type.

    Attributes:
        caption (str | None): Optional caption for the photo.

    """

    caption: str | None = None
