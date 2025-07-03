"""
Media types for the Kamihi bot.

License:
    MIT

"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


@dataclass
class Video(Media):
    """Represents a video media type."""


@dataclass
class Audio(Media):
    """Represents an audio media type."""


class Location:
    """
    Represents a location media type.

    Attributes:
        latitude (float): Latitude of the location, must be between -90 and 90.
        longitude (float): Longitude of the location, must be between -180 and 180.

    """

    def __init__(self, latitude: float, longitude: float) -> None:
        """
        Initialize a Location instance with validated coordinates.

        Args:
            latitude (float): Latitude of the location (-90 to 90).
            longitude (float): Longitude of the location (-180 to 180).

        Raises:
            ValueError: If latitude or longitude values are out of valid range.

        """
        if not -90 <= latitude <= 90:
            msg = f"Latitude must be between -90 and 90, got {latitude}"
            raise ValueError(msg)
        if not -180 <= longitude <= 180:
            msg = f"Longitude must be between -180 and 180, got {longitude}"
            raise ValueError(msg)

        self.latitude = latitude
        self.longitude = longitude

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Location":
        """
        Create a Location instance from a dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing latitude and longitude.

        Returns:
            Location: An instance of Location.

        Raises:
            ValueError: If latitude or longitude values are out of valid range.

        """
        return Location(latitude=data["latitude"], longitude=data["longitude"])

    @staticmethod
    def from_tuple(data: tuple[float, float]) -> "Location":
        """
        Create a Location instance from a tuple.

        Args:
            data (tuple[float, float]): Tuple containing latitude and longitude.

        Returns:
            Location: An instance of Location.

        Raises:
            ValueError: If latitude or longitude values are out of valid range.

        """
        return Location(latitude=data[0], longitude=data[1])

    @staticmethod
    def from_string(data: str) -> "Location":
        """
        Create a Location instance from a string.

        Args:
            data (str): String containing latitude and longitude separated by a comma.

        Returns:
            Location: An instance of Location.

        Raises:
            ValueError: If latitude or longitude values are out of valid range.

        """
        lat, lon = map(float, data.split(","))
        return Location(latitude=lat, longitude=lon)
