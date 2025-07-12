"""
Tests for the media classes in bot.media module.

License:
    MIT

"""

import os
from pathlib import Path

import pytest

from telegram import InputMediaDocument, InputMediaVideo, InputMediaAudio, InputMediaPhoto
from telegram.constants import LocationLimit, FileSizeLimit
from telegramify_markdown import markdownify as md

from kamihi.tg.media import Media, Document, Photo, Video, Audio, Location, Voice


@pytest.fixture
def tmp_image_file_too_large(tmp_image_file):
    """Fixture to create a random image file that exceeds the size limit."""
    chunk_size = 4096  # Add 4KB at a time
    padding_data = b"\x00" * chunk_size  # Null bytes work perfectly as filler

    with open(tmp_image_file, "ab") as f:
        while os.path.getsize(tmp_image_file) <= FileSizeLimit.PHOTOSIZE_UPLOAD + chunk_size:
            f.write(padding_data)

    return tmp_image_file


@pytest.fixture
def tmp_voice_file_too_large(tmp_audio_file):
    """Fixture to create a random audio file that exceeds the size limit."""
    return tmp_audio_file


def test_media_initialization_path(tmp_file):
    """Test that Media class can be initialized with and without optional parameters."""
    media = Media(file=tmp_file, caption="Media caption", filename="media_file.txt")
    assert media.file == tmp_file
    assert media.caption == "Media caption"
    assert media.filename == "media_file.txt"
    assert isinstance(media, Media)


def test_media_initialization_str(tmp_file):
    """Test that Media class can be initialized with a string path."""
    media_str_path = Media(file=str(tmp_file), caption="Media caption")
    assert media_str_path.file == tmp_file
    assert media_str_path.caption == "Media caption"
    assert media_str_path.filename is Path(tmp_file).name
    assert isinstance(media_str_path, Media)


def test_media_initialization_bytes(tmp_file):
    """Test that Media class can be initialized with bytes."""
    media_bytes = Media(file=tmp_file.read_bytes(), caption="Media caption")
    assert media_bytes.caption == "Media caption"
    assert media_bytes.file is not None  # File content should not be None
    assert isinstance(media_bytes, Media)


def test_media_initialization_io(tmp_file):
    """Test that Media class can be initialized with a file-like object."""
    with open(tmp_file, "rb") as file_obj:
        media_io = Media(file=file_obj, caption="Media caption")
        assert media_io.caption == "Media caption"
        assert media_io.file is not None  # File content should not be None
        assert isinstance(media_io, Media)


def test_media_initialization_no_optional(tmp_file):
    """Test that Media class can be initialized without optional parameters."""
    media_no_optional = Media(file=tmp_file)
    assert media_no_optional.file == tmp_file
    assert media_no_optional.caption is None
    assert media_no_optional.filename is Path(tmp_file).name


def test_media_initialization_invalid_path():
    """Test that Media class raises an error for an invalid file path."""
    with pytest.raises(ValueError, match="File /invalid/path/to/file.txt does not exist"):
        Media(file="/invalid/path/to/file.txt")


def test_media_initialization_directory_path(tmp_path):
    """Test that Media class raises an error for a directory path."""
    directory_path = tmp_path / "test_directory"
    directory_path.mkdir()

    with pytest.raises(ValueError, match=f"Path {directory_path} is not a file"):
        Media(file=directory_path)


def test_media_initialization_no_read_permission(tmp_path):
    """Test that Media class raises an error for a file with no read permission."""
    no_read_permission_file = tmp_path / "no_read_permission.txt"
    no_read_permission_file.write_text("This file has no read permission.")

    # Remove read permission
    no_read_permission_file.chmod(0o000)

    with pytest.raises(ValueError, match=f"File {no_read_permission_file} is not readable"):
        Media(file=no_read_permission_file)


def test_media_initialization_exceeds_size_limit(tmp_file):
    """Test that Media class raises an error for files that exceed the size limit."""
    # Create a large file for testing
    large_file = tmp_file.with_name("large_file.txt")
    large_file.write_text("A" * (FileSizeLimit.FILESIZE_UPLOAD + 1))  # Exceeding the size limit

    with pytest.raises(
        ValueError, match=f"File {large_file} exceeds the size limit of {float(FileSizeLimit.FILESIZE_UPLOAD)} bytes"
    ):
        Media(file=large_file)


def test_media_initialization_exceeds_size_limit_bytes(tmp_file):
    """Test that Media class raises an error for files that exceed the size limit."""
    # Create a large file for testing
    large_file = tmp_file.with_name("large_file.txt")
    large_file.write_text("A" * (FileSizeLimit.FILESIZE_UPLOAD + 1))  # Exceeding the size limit

    with pytest.raises(
        ValueError, match=f"Byte data exceeds the size limit of {float(FileSizeLimit.FILESIZE_UPLOAD)} bytes"
    ):
        Media(file=large_file.read_bytes())


def test_document_initialization(tmp_file):
    """Test that Document class can be initialized correctly."""
    document = Document(file=tmp_file, caption="Document caption")
    assert document.file == tmp_file
    assert document.caption == "Document caption"
    assert isinstance(document, Media)


def test_document_as_input_media(tmp_file):
    """Test that Document class can be converted to InputMediaDocument."""
    document = Document(file=tmp_file, caption="Document caption")
    input_media = document.as_input_media()
    assert isinstance(input_media, InputMediaDocument)
    assert input_media.media.input_file_content == tmp_file.read_bytes()
    assert input_media.caption == md("Document caption")


def test_photo_initialization(tmp_image_file):
    """Test that Photo class can be initialized correctly."""
    photo = Photo(file=tmp_image_file, caption="Photo caption")
    assert photo.file == tmp_image_file
    assert photo.caption == "Photo caption"


def test_photo_initialization_too_large(tmp_image_file_too_large):
    """Test that Photo class raises an error for files that exceed the size limit."""
    with pytest.raises(
        ValueError,
        match=f"File {tmp_image_file_too_large} exceeds the size limit of {float(FileSizeLimit.PHOTOSIZE_UPLOAD)} bytes",
    ):
        Photo(file=tmp_image_file_too_large)


def test_photo_as_input_media(tmp_file):
    """Test that Photo class can be converted to InputMediaPhoto."""
    photo = Photo(file=tmp_file, caption="Photo caption")
    input_media = photo.as_input_media()
    assert isinstance(input_media, InputMediaPhoto)
    assert input_media.caption == md("Photo caption")
    assert input_media.media.input_file_content == tmp_file.read_bytes()


def test_video_initialization(tmp_video_file):
    """Test that Video class can be initialized correctly."""
    video = Video(file=tmp_video_file, caption="Video caption")
    assert video.file == tmp_video_file
    assert video.caption == "Video caption"
    assert isinstance(video, Media)


def test_video_as_input_media(tmp_file):
    """Test that Video class can be converted to InputMediaVideo."""
    video = Video(file=tmp_file, caption="Video caption")
    input_media = video.as_input_media()
    assert isinstance(input_media, InputMediaVideo)
    assert input_media.caption == md("Video caption")
    assert input_media.media.input_file_content == tmp_file.read_bytes()


def test_audio_initialization(tmp_audio_file):
    """Test that Audio class can be initialized correctly."""
    audio = Audio(file=tmp_audio_file, caption="Audio caption")
    assert audio.file == tmp_audio_file
    assert audio.caption == "Audio caption"
    assert isinstance(audio, Media)


def test_audio_as_input_media(tmp_file):
    """Test that Audio class can be converted to InputMediaAudio."""
    audio = Audio(file=tmp_file, caption="Audio caption")
    input_media = audio.as_input_media()
    assert isinstance(input_media, InputMediaAudio)
    assert input_media.caption == md("Audio caption")
    assert input_media.media.input_file_content == tmp_file.read_bytes()


def test_voice_initialization(tmp_voice_file):
    """Test that Voice class can be initialized correctly."""
    voice = Voice(file=tmp_voice_file, caption="Voice caption")
    assert voice.file == tmp_voice_file
    assert voice.caption == "Voice caption"
    assert isinstance(voice, Media)


def test_voice_too_large(tmp_voice_file_too_large):
    """Test that Voice class raises an error for files that exceed the size limit."""
    with pytest.raises(
        ValueError,
        match=f"File {tmp_voice_file_too_large} exceeds the size limit of {float(FileSizeLimit.VOICE_NOTE_FILE_SIZE)} bytes",
    ):
        Voice(file=tmp_voice_file_too_large, caption="Voice caption")


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
