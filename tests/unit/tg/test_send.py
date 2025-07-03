"""
Tests for the kamihi.tg.send module.

This module contains unit tests for the send_text, send_file, send, and reply functions
used to send messages via the Telegram API.

License:
    MIT
"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

from loguru import logger
import pytest
from logot import Logot, logged
from telegram import Bot, Message, Update
from telegram.constants import FileSizeLimit
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

from kamihi.tg.send import send_text, send_document, _check_path, send_photo, send_video
from tests.conftest import random_image


@pytest.fixture
def mock_ptb_bot():
    """Fixture to provide a mock Bot instance."""
    bot = Mock(spec=Bot)
    bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    bot.send_document = AsyncMock(return_value=Mock(spec=Message))
    bot.send_photo = AsyncMock(return_value=Mock(spec=Message))
    bot.send_video = AsyncMock(return_value=Mock(spec=Message))
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


@pytest.mark.asyncio
async def test_send_text(logot: Logot, mock_update, mock_context):
    """Test basic functionality of send_text with minimal parameters."""
    text = "Test message"

    # Call function
    await send_text(text, update=mock_update, context=mock_context)

    # Verify send_message was called with correct parameters
    mock_context.bot.send_message.assert_called_once_with(
        mock_update.effective_chat.id,
        md(text),
    )

    # Verify that the logger was called
    logot.assert_logged(logged.debug("Message sent"))


@pytest.mark.asyncio
async def test_send_text_error_handling(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test that send_text properly catches and logs TelegramError."""
    text = "Test message"

    # Make send_message raise a TelegramError
    mock_ptb_bot.send_message.side_effect = TelegramError("Test error")

    # Call function
    await send_text(text, update=mock_update, context=mock_context)

    # Verify send_message was called with correct parameters
    mock_context.bot.send_message.assert_called_once_with(
        mock_update.effective_chat.id,
        md(text),
    )

    # Verify that the logger was called
    logot.assert_logged(logged.error("Failed to send message"))


def test_check_path(tmp_file):
    """Test that send_file handles invalid Path content."""
    # Call function
    result = _check_path(tmp_file, logger)

    # Verify that error was not logged
    assert result is True


def test_check_path_with_invalid_path(logot: Logot):
    """Test that send_file handles invalid Path content."""
    invalid_path = Path("invalid/path/to/file.txt")

    # Call function
    result = _check_path(invalid_path, logger)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("File does not exist"))
    # Verify function returns None
    assert result is False


def test_check_path_with_directory_path(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles directory Path content."""
    # Call function
    result = _check_path(tmp_path, logger)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("Path is not a file"))
    # Verify function returns None
    assert result is False


def test_check_path_with_no_read_permission(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles no read permission for file."""
    no_permission_file = tmp_path / "no_permission_file.txt"
    no_permission_file.write_text("This file has no read permission.")

    # Remove read permissions
    no_permission_file.chmod(0o000)

    # Call function
    result = _check_path(no_permission_file, logger)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("No read permission for file"))
    # Verify function returns None
    assert result is False


def test_check_path_empty_file(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles empty file content."""
    empty_file = tmp_path / "empty_file.txt"
    empty_file.write_text("")

    # Call function
    result = _check_path(empty_file, logger)

    # Verify that the logger was called with a debug message
    logot.assert_logged(logged.debug("File is empty, but sending anyway"))
    # Verify function returns True
    assert result is True


def test_check_path_file_too_big(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles files that are too big."""
    too_big_file = tmp_path / "too_big_file.txt"
    too_big_file.write_text("A" * (FileSizeLimit.FILESIZE_UPLOAD + 1))

    # Call function
    result = _check_path(too_big_file, logger)
    # Verify that the logger was called with an error
    logot.assert_logged(
        logged.error(
            f"File size ({too_big_file.stat().st_size} bytes) exceeds Telegram limit of {FileSizeLimit.FILESIZE_UPLOAD} bytes"
        )
    )
    # Verify function returns False
    assert result is False


@pytest.mark.asyncio
async def test_send_document(logot: Logot, tmp_file, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_file with minimal parameters."""
    # Call function
    await send_document(tmp_file, update=mock_update, context=mock_context)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        document=tmp_file,
        filename=tmp_file.name,
        caption=None,
    )
    logot.assert_logged(logged.debug("File sent"))


@pytest.mark.asyncio
async def test_send_document_invalid(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_file with minimal parameters."""
    invalid_path = Path("invalid/path/to/file.txt")

    # Call function
    result = await send_document(invalid_path, update=mock_update, context=mock_context)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("File does not exist"))
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_document_telegram_error_handling(logot: Logot, mock_ptb_bot, tmp_file, mock_update, mock_context):
    """Test that send_document properly catches and logs TelegramError."""
    # Make send_document raise a TelegramError
    mock_ptb_bot.send_document.side_effect = TelegramError("Test error")

    # Call function
    result = await send_document(tmp_file, update=mock_update, context=mock_context)

    # Verify that the logger was called
    logot.assert_logged(logged.error("Failed to send file"))
    assert result is None


@pytest.mark.asyncio
async def test_send_photo(logot: Logot, tmp_image_file, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_photo with minimal parameters."""
    # Call function
    result = await send_photo(tmp_image_file, update=mock_update, context=mock_context)

    # Verify send_photo was called with correct parameters
    mock_ptb_bot.send_photo.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        photo=tmp_image_file,
        caption=None,
        filename=tmp_image_file.name,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Photo sent"))


@pytest.mark.asyncio
async def test_send_photo_invalid(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test that send_photo handles invalid Path content."""
    invalid_path = Path("invalid/path/to/file.jpg")

    # Call function
    result = await send_photo(invalid_path, update=mock_update, context=mock_context)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("File does not exist"))
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_photo_telegram_error_handling(
    logot: Logot, mock_ptb_bot, tmp_image_file, mock_update, mock_context
):
    """Test that send_photo properly catches and logs TelegramError."""
    # Make send_photo raise a TelegramError
    mock_ptb_bot.send_photo.side_effect = TelegramError("Test error")

    # Call function
    result = await send_photo(tmp_image_file, update=mock_update, context=mock_context)

    # Verify that the logger was called
    logot.assert_logged(logged.error("Failed to send photo"))
    assert result is None


@pytest.mark.asyncio
async def test_send_video(logot: Logot, random_video_path, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_video with minimal parameters."""
    # Call function
    result = await send_video(random_video_path, update=mock_update, context=mock_context)

    # Verify send_video was called with correct parameters
    mock_ptb_bot.send_video.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        video=random_video_path,
        caption=None,
        filename=random_video_path.name,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Video sent"))


@pytest.mark.asyncio
async def test_send_video_invalid(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test that send_video handles invalid Path content."""
    invalid_path = Path("invalid/path/to/file.mp4")

    # Call function
    result = await send_video(invalid_path, update=mock_update, context=mock_context)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("File does not exist"))
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_video_telegram_error_handling(
    logot: Logot, mock_ptb_bot, random_video_path, mock_update, mock_context
):
    """Test that send_video properly catches and logs TelegramError."""
    # Make send_video raise a TelegramError
    mock_ptb_bot.send_video.side_effect = TelegramError("Test error")

    # Call function
    result = await send_video(random_video_path, update=mock_update, context=mock_context)

    # Verify that the logger was called
    logot.assert_logged(logged.error("Failed to send video"))
    assert result is None


@pytest.mark.asyncio
async def test_send_video_invalid_mime_type(logot: Logot, mock_ptb_bot, mock_update, mock_context, tmp_path):
    """Test that send_video handles invalid MIME type."""
    invalid_video = tmp_path / "invalid_video.txt"
    invalid_video.write_text("This is not a video file.")

    # Call function
    result = await send_video(invalid_video, update=mock_update, context=mock_context)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("File is not a valid MP4 video"))
    # Verify function returns None
    assert result is None
