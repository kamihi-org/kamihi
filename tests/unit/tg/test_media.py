"""
Tests for the media classes in bot.media module.

License:
    MIT

"""

import pytest
from pathlib import Path

from telegram import InputMediaDocument, InputMediaVideo, InputMediaAudio, InputMediaPhoto
from telegram.constants import LocationLimit
from telegramify_markdown import markdownify as md

from kamihi.tg.media import Media, Document, Photo, Video, Audio, Location


def test_media_initialization(tmp_file):
    """Test that Media class can be initialized with and without optional parameters."""
    media = Media(path=tmp_file, caption="Media caption", filename="media_file.txt")
    assert media.path == tmp_file
    assert media.caption == "Media caption"
    assert media.filename == "media_file.txt"
    assert isinstance(media, Media)


def test_media_initialization_no_optional(tmp_file):
    """Test that Media class can be initialized without optional parameters."""
    media_no_optional = Media(path=tmp_file)
    assert media_no_optional.path == tmp_file
    assert media_no_optional.caption is None
    assert media_no_optional.filename is None


def test_media_filename(tmp_file):
    """Test that Media class can derive filename from path."""
    media = Media(path=tmp_file)
    assert media._get_filename() == tmp_file.name


def test_media_filename_with_custom_name(tmp_file):
    """Test with a filename set explicitly."""
    media_with_filename = Media(path=tmp_file, filename="custom_name.txt")
    assert media_with_filename._get_filename() == "custom_name.txt"


def test_media_filename_with_no_path():
    """Test that Media class returns None for filename when path is not a string or Path."""
    media_str_path = Media(path="/s/t/r/path")
    assert media_str_path._get_filename() is None


def test_document_initialization(tmp_file):
    """Test that Document class can be initialized correctly."""
    document = Document(path=tmp_file, caption="Document caption")
    assert document.path == tmp_file
    assert document.caption == "Document caption"
    assert isinstance(document, Media)


def test_document_as_input_media(tmp_file):
    """Test that Document class can be converted to InputMediaDocument."""
    document = Document(path=tmp_file, caption="Document caption")
    input_media = document.as_input_media()
    assert isinstance(input_media, InputMediaDocument)
    assert input_media.media.input_file_content == tmp_file.read_bytes()
    assert input_media.caption == md("Document caption")


def test_photo_initialization():
    """Test that Photo class can be initialized correctly."""
    path = Path("/path/to/photo.jpg")
    photo = Photo(path=path, caption="Photo caption")
    assert photo.path == path
    assert photo.caption == "Photo caption"
    assert isinstance(photo, Media)


def test_photo_as_input_media(tmp_file):
    """Test that Photo class can be converted to InputMediaPhoto."""
    photo = Photo(path=tmp_file, caption="Photo caption")
    input_media = photo.as_input_media()
    assert isinstance(input_media, InputMediaPhoto)
    assert input_media.caption == md("Photo caption")
    assert input_media.media.input_file_content == tmp_file.read_bytes()


def test_video_initialization():
    """Test that Video class can be initialized correctly."""
    path = Path("/path/to/video.mp4")
    video = Video(path=path, caption="Video caption")
    assert video.path == path
    assert video.caption == "Video caption"
    assert isinstance(video, Media)


def test_video_as_input_media(tmp_file):
    """Test that Video class can be converted to InputMediaVideo."""
    video = Video(path=tmp_file, caption="Video caption")
    input_media = video.as_input_media()
    assert isinstance(input_media, InputMediaVideo)
    assert input_media.caption == md("Video caption")
    assert input_media.media.input_file_content == tmp_file.read_bytes()


def test_audio_initialization():
    """Test that Audio class can be initialized correctly."""
    path = Path("/path/to/audio.mp3")
    audio = Audio(path=path, caption="Audio caption")
    assert audio.path == path
    assert audio.caption == "Audio caption"
    assert isinstance(audio, Media)


def test_audio_as_input_media(tmp_file):
    """Test that Audio class can be converted to InputMediaAudio."""
    audio = Audio(path=tmp_file, caption="Audio caption")
    input_media = audio.as_input_media()
    assert isinstance(input_media, InputMediaAudio)
    assert input_media.caption == md("Audio caption")
    assert input_media.media.input_file_content == tmp_file.read_bytes()


def test_location_initialization():
    """Test that Location class can be initialized correctly."""
    location = Location(latitude=35.6895, longitude=139.6917)
    assert location.latitude == 35.6895
    assert location.longitude == 139.6917


@pytest.mark.parametrize(
    "latitude,longitude,horizontal_accuracy,should_raise",
    [
        (35.6895, 139.6917, None, False),  # Valid coordinates
        (-33.8688, -151.2093, None, False),  # Valid negative coordinates
        (0, 0, None, False),  # Zero coordinates
        (90, 180, None, False),  # Extreme valid coordinates
        (-90, -180, None, False),  # Extreme valid coordinates
        (35.6895, 139.6917, 10, False),  # Valid with horizontal accuracy
        (35.6895, 139.6917, 0, False),  # Valid with zero horizontal accuracy
        (35.6895, 139.6917, LocationLimit.HORIZONTAL_ACCURACY, False),  # Valid with high horizontal accuracy
        (91, 0, 0, True),  # Invalid latitude (too high)
        (-91, 0, 0, True),  # Invalid latitude (too low)
        (0, 181, 0, True),  # Invalid longitude (too high)
        (0, -181, 0, True),  # Invalid longitude (too low)
        (35.6895, 139.6917, LocationLimit.HORIZONTAL_ACCURACY + 1, True),  # Invalid horizontal accuracy (too high)
        (35.6895, 139.6917, -1, True),  # Invalid horizontal accuracy (too low)
    ],
)
def test_location_validation(latitude, longitude, horizontal_accuracy, should_raise):
    """Test validation of latitude and longitude values."""
    if should_raise:
        with pytest.raises(ValueError):
            Location(latitude=latitude, longitude=longitude, horizontal_accuracy=horizontal_accuracy)
    else:
        location = Location(latitude=latitude, longitude=longitude, horizontal_accuracy=horizontal_accuracy)
        assert location.latitude == latitude
        assert location.longitude == longitude
