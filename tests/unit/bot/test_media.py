"""
Tests for the media classes in bot.media module.

License:
    MIT

"""

import pytest
from pathlib import Path

from kamihi.bot.media import Media, Document, Photo, Video, Audio, Location


def test_media_initialization():
    """Test that Media class can be initialized with and without optional parameters."""
    # Basic initialization without parameters
    media = Media()
    assert media.path is None
    assert media.caption is None

    # Initialization with parameters
    path = Path("/path/to/file.txt")
    caption = "Sample caption"
    media = Media(path=path, caption=caption)
    assert media.path == path
    assert media.caption == caption


def test_document_initialization():
    """Test that Document class can be initialized correctly."""
    path = Path("/path/to/document.pdf")
    document = Document(path=path, caption="Document caption")
    assert document.path == path
    assert document.caption == "Document caption"
    assert isinstance(document, Media)


def test_photo_initialization():
    """Test that Photo class can be initialized correctly."""
    path = Path("/path/to/photo.jpg")
    photo = Photo(path=path, caption="Photo caption")
    assert photo.path == path
    assert photo.caption == "Photo caption"
    assert isinstance(photo, Media)


def test_video_initialization():
    """Test that Video class can be initialized correctly."""
    path = Path("/path/to/video.mp4")
    video = Video(path=path, caption="Video caption")
    assert video.path == path
    assert video.caption == "Video caption"
    assert isinstance(video, Media)


def test_audio_initialization():
    """Test that Audio class can be initialized correctly."""
    path = Path("/path/to/audio.mp3")
    audio = Audio(path=path, caption="Audio caption")
    assert audio.path == path
    assert audio.caption == "Audio caption"
    assert isinstance(audio, Media)


def test_location_initialization():
    """Test that Location class can be initialized correctly."""
    location = Location(latitude=35.6895, longitude=139.6917)
    assert location.latitude == 35.6895
    assert location.longitude == 139.6917


def test_location_from_dict():
    """Test creating Location from dictionary."""
    location_dict = {"latitude": 35.6895, "longitude": 139.6917}
    location = Location.from_dict(location_dict)
    assert location.latitude == 35.6895
    assert location.longitude == 139.6917


def test_location_from_tuple():
    """Test creating Location from tuple."""
    location_tuple = (35.6895, 139.6917)
    location = Location.from_tuple(location_tuple)
    assert location.latitude == 35.6895
    assert location.longitude == 139.6917


@pytest.mark.parametrize(
    "coordinate_string,expected_latitude,expected_longitude",
    [
        ("35.6895,139.6917", 35.6895, 139.6917),  # Both positive
        ("-33.8688,-151.2093", -33.8688, -151.2093),  # Both negative
        ("37.7749,-122.4194", 37.7749, -122.4194),  # Positive lat, negative long
        ("-34.6037,58.3816", -34.6037, 58.3816),  # Negative lat, positive long
        ("0,0", 0, 0),  # Zero coordinates
        ("-90,180", -90, 180),  # Extreme valid coordinates
        ("90,-180", 90, -180),  # Extreme valid coordinates opposite
    ],
)
def test_location_from_string(coordinate_string, expected_latitude, expected_longitude):
    """Test creating Location from string with various coordinate combinations."""
    location = Location.from_string(coordinate_string)
    assert location.latitude == expected_latitude
    assert location.longitude == expected_longitude


@pytest.mark.parametrize(
    "latitude,longitude,should_raise",
    [
        (35.6895, 139.6917, False),  # Valid coordinates
        (-33.8688, -151.2093, False),  # Valid negative coordinates
        (0, 0, False),  # Zero coordinates
        (90, 180, False),  # Extreme valid coordinates
        (-90, -180, False),  # Extreme valid coordinates
        (91, 0, True),  # Invalid latitude (too high)
        (-91, 0, True),  # Invalid latitude (too low)
        (0, 181, True),  # Invalid longitude (too high)
        (0, -181, True),  # Invalid longitude (too low)
    ],
)
def test_location_validation(latitude, longitude, should_raise):
    """Test validation of latitude and longitude values."""
    if should_raise:
        with pytest.raises(ValueError):
            Location(latitude=latitude, longitude=longitude)
    else:
        location = Location(latitude=latitude, longitude=longitude)
        assert location.latitude == latitude
        assert location.longitude == longitude


def test_location_factory_methods_validation():
    """Test that factory methods correctly validate coordinates."""
    # Invalid coordinates through dictionary
    with pytest.raises(ValueError):
        Location.from_dict({"latitude": 100, "longitude": 50})

    # Invalid coordinates through tuple
    with pytest.raises(ValueError):
        Location.from_tuple((50, 200))

    # Invalid coordinates through string
    with pytest.raises(ValueError):
        Location.from_string("-100,30")
