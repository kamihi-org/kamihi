"""
Tests for the kamihi.tg.send module.

This module contains unit tests for the send_text, send_file, send, and reply functions
used to send messages via the Telegram API.

License:
    MIT
"""

import random
from unittest.mock import AsyncMock, Mock, MagicMock

import pytest
from logot import Logot, logged
from telegram import Bot, Message, Update
from telegram.constants import FileSizeLimit
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

from kamihi.tg.media import *
from kamihi.tg.send import check_file, send
from tests.conftest import random_image, random_video_path, random_audio


@pytest.fixture
def mock_ptb_bot():
    """Fixture to provide a mock Bot instance."""
    bot = Mock(spec=Bot)
    bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    bot.send_document = AsyncMock(return_value=Mock(spec=Message))
    bot.send_photo = AsyncMock(return_value=Mock(spec=Message))
    bot.send_video = AsyncMock(return_value=Mock(spec=Message))
    bot.send_audio = AsyncMock(return_value=Mock(spec=Message))
    return bot


@pytest.fixture
def mock_update():
    """Fixture to provide a mock Update object."""
    update = Mock(spec=Update)
    update.effective_message = Mock()
    update.effective_message.message_id = 789
    update.effective_chat = Mock()
    update.effective_chat.id = 123456
    return update


@pytest.fixture
def mock_context(mock_ptb_bot):
    """Fixture to provide a mock CallbackContext."""
    context = Mock(spec=CallbackContext)
    context.bot = mock_ptb_bot
    return context


@pytest.fixture
def tmp_file(tmp_path):
    """Fixture to provide a mock file path."""
    file = tmp_path / "test_file.txt"
    file.write_text("This is a test file.")
    return file


@pytest.fixture
def tmp_image_file(tmp_path):
    """Fixture to create a random image in a temporal directory and provide its path."""
    file = tmp_path / "test_file.jpg"

    with open(file, "wb") as f:
        f.write(random_image())

    return file


@pytest.fixture
def tmp_video_file(tmp_path):
    """Fixture that provides a random video file path."""
    return random_video_path()


@pytest.fixture
def tmp_audio_file(tmp_path):
    """Fixture that provides a random audio file path."""
    fmt = random.choice(["m4a"])
    audio_path = tmp_path / f"test_audio.{fmt}"
    audio_data = random_audio(output_format=fmt)
    with open(audio_path, "wb") as f:
        f.write(audio_data)
    return audio_path


@pytest.fixture
def random_location():
    """Fixture to provide a random Location object."""
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    return Location(latitude=latitude, longitude=longitude)


def test_check_file(tmp_file):
    """Test that send_file handles invalid Path content."""
    # Call function, it should not raise an error
    check_file(tmp_file)


def test_check_file_with_invalid_path(logot: Logot):
    """Test that send_file handles invalid Path content."""
    invalid_path = Path("invalid/path/to/file.txt")

    # Call function
    with pytest.raises(ValueError, match=f"File {invalid_path} does not exist"):
        check_file(invalid_path)


def test_check_file_with_directory_path(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles directory Path content."""
    # Call function
    with pytest.raises(ValueError, match=f"Path {tmp_path} is not a file"):
        check_file(tmp_path)


def test_check_file_with_no_read_permission(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles no read permission for file."""
    no_permission_file = tmp_path / "no_permission_file.txt"
    no_permission_file.write_text("This file has no read permission.")

    # Remove read permissions
    no_permission_file.chmod(0o000)

    # Call function
    with pytest.raises(ValueError, match=f"File {no_permission_file} is not readable"):
        check_file(no_permission_file)


@pytest.mark.asyncio
async def test_send_text(logot: Logot, mock_update, mock_context):
    """Test basic functionality of send_text with minimal parameters."""
    text = "Test message"

    # Call function
    await send(text, update=mock_update, context=mock_context)

    # Verify send_message was called with correct parameters
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=md(text),
    )

    # Verify that the logger was called
    logot.assert_logged(logged.debug("Sending as text message"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_error_handling(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test that send_text properly catches and logs TelegramError."""
    text = "Test message"

    # Make send_message raise a TelegramError
    mock_ptb_bot.send_message.side_effect = TelegramError("Test error")

    # Call function
    await send(text, update=mock_update, context=mock_context)

    # Verify send_message was called with correct parameters
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text=md(text),
    )

    # Verify that the logger was called
    logot.assert_logged(logged.debug("Sending as text message"))
    logot.assert_logged(logged.error("Failed to send"))


@pytest.mark.asyncio
async def test_send_path_photo(logot: Logot, tmp_image_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending a photo using just the path."""
    # Call function
    result = await send(tmp_image_file, update=mock_update, context=mock_context)

    # Verify send_photo was called with correct parameters
    mock_ptb_bot.send_photo.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        photo=tmp_image_file,
        filename=tmp_image_file.name,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as photo"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_video(logot: Logot, tmp_video_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending a video using just the path."""
    # Call function
    result = await send(tmp_video_file, update=mock_update, context=mock_context)

    # Verify send_video was called with correct parameters
    mock_ptb_bot.send_video.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        video=tmp_video_file,
        filename=tmp_video_file.name,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as video"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_audio(logot: Logot, tmp_audio_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending an audio file using just the path."""
    # Call function
    result = await send(tmp_audio_file, update=mock_update, context=mock_context)

    # Verify send_audio was called with correct parameters
    mock_ptb_bot.send_audio.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        audio=tmp_audio_file,
        filename=tmp_audio_file.name,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as audio"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_document(logot: Logot, tmp_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending a file using just the path."""
    # Call function
    result = await send(tmp_file, update=mock_update, context=mock_context)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        document=tmp_file,
        filename=tmp_file.name,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as generic file"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_invalid(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test sending an invalid Path."""
    invalid_path = Path("invalid/path/to/file.txt")

    # Call function
    with pytest.raises(ValueError, match=f"File {invalid_path} does not exist"):
        await send(invalid_path, update=mock_update, context=mock_context)


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", [None, md("Test caption")])
async def test_send_media_document(logot: Logot, tmp_file, caption, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_file with minimal parameters."""
    # Call function
    await send(Document(tmp_file, caption=caption), update=mock_update, context=mock_context)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        document=tmp_file,
        filename=tmp_file.name,
        caption=(caption),
    )
    logot.assert_logged(logged.debug("Sending as generic file"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", [None, md("Test caption")])
async def test_send_media_photo(logot: Logot, tmp_image_file, caption, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_photo with minimal parameters."""
    # Call function
    await send(Photo(tmp_image_file, caption=caption), update=mock_update, context=mock_context)

    # Verify send_photo was called with correct parameters
    mock_ptb_bot.send_photo.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        photo=tmp_image_file,
        filename=tmp_image_file.name,
        caption=caption,
    )
    logot.assert_logged(logged.debug("Sending as photo"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", [None, md("Test caption")])
async def test_send_media_video(logot: Logot, tmp_video_file, caption, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_video with minimal parameters."""
    # Call function
    await send(Video(tmp_video_file, caption=caption), update=mock_update, context=mock_context)

    # Verify send_video was called with correct parameters
    mock_ptb_bot.send_video.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        video=tmp_video_file,
        filename=tmp_video_file.name,
        caption=caption,
    )
    logot.assert_logged(logged.debug("Sending as video"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", [None, md("Test caption")])
async def test_send_media_audio(logot: Logot, tmp_audio_file, caption, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_audio with minimal parameters."""
    # Call function
    await send(Audio(tmp_audio_file, caption=caption), update=mock_update, context=mock_context)

    # Verify send_audio was called with correct parameters
    mock_ptb_bot.send_audio.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        audio=tmp_audio_file,
        filename=tmp_audio_file.name,
        caption=caption,
    )
    logot.assert_logged(logged.debug("Sending as audio"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_media_invalid(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test sending an invalid Media object."""
    invalid_path = Path("invalid/path/to/file.txt")

    # Call function
    with pytest.raises(ValueError, match=f"File {invalid_path} does not exist"):
        await send(Document(invalid_path), update=mock_update, context=mock_context)


@pytest.mark.asyncio
async def test_send_location(logot: Logot, random_location, mock_ptb_bot, mock_update, mock_context):
    """Test sending a Location object."""
    location = random_location

    # Call function
    await send(location, update=mock_update, context=mock_context)

    # Verify send_location was called with correct parameters
    mock_ptb_bot.send_location.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        latitude=location.latitude,
        longitude=location.longitude,
    )
    logot.assert_logged(logged.debug("Sending as location"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_list(logot: Logot, tmp_file, tmp_image_file, mock_update, mock_context):
    """Test sending a list of mixed objects."""
    items = [tmp_file, Photo(tmp_image_file, caption="Test caption"), "Test message"]

    # Call function
    results = await send(items, update=mock_update, context=mock_context)

    # Verify that send was called for each item
    assert len(results) == 3
    mock_context.bot.send_document.assert_called_with(
        chat_id=mock_update.effective_chat.id,
        document=tmp_file,
        filename=tmp_file.name,
    )
    mock_context.bot.send_photo.assert_called_with(
        chat_id=mock_update.effective_chat.id,
        photo=tmp_image_file,
        filename=tmp_image_file.name,
        caption=md("Test caption"),
    )
    mock_context.bot.send_message.assert_called_with(
        chat_id=mock_update.effective_chat.id,
        text=md("Test message"),
    )
    logot.assert_logged(logged.debug("Sending as list of items"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_invalid_type(logot: Logot, mock_update, mock_context):
    """Test sending an unsupported object type."""
    invalid_obj = object()

    # Call function
    with pytest.raises(TypeError, match=f"Object of type {type(invalid_obj)} cannot be sent"):
        await send(invalid_obj, update=mock_update, context=mock_context)
