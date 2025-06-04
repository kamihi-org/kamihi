"""
Tests for the kamihi.tg.send module.

This module contains unit tests for the send_text, send_file, send, and reply functions
used to send messages via the Telegram API.

License:
    MIT
"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from logot import Logot, logged
from telegram import Bot, Message, Update
from telegram.constants import FileSizeLimit
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

from kamihi.tg.send import reply, send, send_file, send_text


@pytest.fixture
def mock_ptb_bot():
    """Fixture to provide a mock Bot instance."""
    bot = Mock(spec=Bot)
    bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    bot.send_document = AsyncMock(return_value=Mock(spec=Message))
    return bot


@pytest.fixture
def tmp_file(tmp_path):
    """Fixture to provide a mock file path."""
    file = tmp_path / "test_file.txt"
    file.write_text("This is a test file.")
    return file


@pytest.fixture
def mock_update_context():
    """Fixture to provide mock Update and CallbackContext."""
    update = Mock(spec=Update)
    context = Mock(spec=CallbackContext)

    # Set up effective_message
    mock_message = Mock()
    mock_message.chat_id = 123456
    mock_message.message_id = 789
    update.effective_message = mock_message

    # Set up context.bot
    bot = Mock(spec=Bot)
    bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    bot.send_document = AsyncMock(return_value=Mock(spec=Message))
    context.bot = bot

    return update, context


@pytest.mark.asyncio
async def test_send_text_basic(logot: Logot, mock_ptb_bot):
    """Test basic functionality of send_text with minimal parameters."""
    # Configure return value for send_message
    mock_message = Mock(spec=Message)
    mock_ptb_bot.send_message.return_value = mock_message

    chat_id = 123456
    text = "Test message"

    # Call function
    await send_text(mock_ptb_bot, chat_id, text)

    # Verify send_message was called with correct parameters
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(text), reply_to_message_id=None)
    logot.assert_logged(logged.debug("Message sent"))


@pytest.mark.asyncio
async def test_send_text_with_reply(logot: Logot, mock_ptb_bot):
    """Test that send_text correctly handles reply_to_message_id parameter."""
    chat_id = 123456
    text = "Reply message"
    reply_to = 789

    # Call function
    await send_text(mock_ptb_bot, chat_id, text, reply_to)

    # Verify send_message was called with reply_to_message_id parameter set to reply_to
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(text), reply_to_message_id=reply_to)
    logot.assert_logged(logged.debug("Reply sent"))


@pytest.mark.asyncio
async def test_send_text_with_markdown_formatting(logot: Logot, mock_ptb_bot):
    """Test that send_text correctly sends messages with Markdown formatting."""
    chat_id = 123456
    markdown_text = "*Bold text* and _italic text_"

    # Call function
    await send_text(mock_ptb_bot, chat_id, markdown_text)

    # Verify Markdown text is preserved when sending
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(markdown_text), reply_to_message_id=None)
    logot.assert_logged(logged.debug("Message sent"))


@pytest.mark.asyncio
async def test_send_text_with_special_markdown_characters(logot: Logot, mock_ptb_bot):
    """Test that send_text correctly handles special Markdown characters."""
    chat_id = 123456
    text_with_special_chars = "Special characters: *asterisks*, _underscores_, `backticks`"

    # Call function
    await send_text(mock_ptb_bot, chat_id, text_with_special_chars)

    # Verify text with special characters is sent correctly
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(text_with_special_chars), reply_to_message_id=None)
    logot.assert_logged(logged.debug("Message sent"))


@pytest.mark.asyncio
async def test_send_text_with_complex_markdown(logot: Logot, mock_ptb_bot):
    """Test that send_text correctly handles complex Markdown formatting."""
    chat_id = 123456
    complex_markdown = "_*Bold inside italic*_ and *_Italic inside bold_*."

    # Call function
    await send_text(mock_ptb_bot, chat_id, complex_markdown)

    # Verify complex markdown is preserved
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(complex_markdown), reply_to_message_id=None)
    logot.assert_logged(logged.debug("Message sent"))


@pytest.mark.asyncio
async def test_send_text_error_handling(logot: Logot, mock_ptb_bot):
    """Test that send_text properly catches and logs TelegramError."""
    chat_id = 123456
    text = "Test message"

    # Make send_message raise a TelegramError
    mock_ptb_bot.send_message.side_effect = TelegramError("Test error")

    # Call the function (should not raise now because context manager swallows exception)
    result = await send_text(mock_ptb_bot, chat_id, text)

    # Verify that the logger was called
    logot.assert_logged(logged.error("Failed to send message"))
    assert result is None


@pytest.mark.asyncio
async def test_send_text_handles_markdown_errors(logot: Logot, mock_ptb_bot):
    """Test that send_text properly handles malformed Markdown content."""
    chat_id = 123456
    malformed_markdown = "This has *unclosed bold"

    # Make send_message raise a TelegramError for malformed markdown
    error = TelegramError("Bad markdown formatting")
    mock_ptb_bot.send_message.side_effect = error

    # Call the function (should not raise now because context manager swallows exception)
    result = await send_text(mock_ptb_bot, chat_id, malformed_markdown)

    # Verify that the logger was called
    logot.assert_logged(logged.error("Failed to send message"))
    assert result is None


@pytest.mark.asyncio
async def test_send_file(logot: Logot, mock_ptb_bot, tmp_file):
    """Test basic functionality of send_file with minimal parameters."""
    # Configure return value for send_document
    mock_message = Mock(spec=Message)
    mock_message.message_id = 123
    mock_ptb_bot.send_document.return_value = mock_message

    chat_id = 123456

    # Call function
    result = await send_file(mock_ptb_bot, chat_id, tmp_file)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=chat_id,
        document=tmp_file,
        filename=tmp_file.name,
        reply_to_message_id=None,
    )
    assert result == mock_message
    logot.assert_logged(logged.debug("File sent"))


@pytest.mark.asyncio
async def test_send_file_with_reply(logot: Logot, mock_ptb_bot, tmp_file):
    """Test that send_file correctly handles reply_to_message_id parameter."""
    chat_id = 123456
    reply_to = 789

    # Call function
    await send_file(mock_ptb_bot, chat_id, tmp_file, reply_to)

    # Verify send_document was called with reply_to_message_id parameter
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=chat_id,
        document=tmp_file,
        filename=tmp_file.name,
        reply_to_message_id=reply_to,
    )
    logot.assert_logged(logged.debug("File sent"))


@pytest.mark.asyncio
async def test_send_file_telegram_error_handling(logot: Logot, mock_ptb_bot, tmp_file):
    """Test that send_file properly catches and logs TelegramError."""
    chat_id = 123456

    # Make send_document raise a TelegramError
    mock_ptb_bot.send_document.side_effect = TelegramError("Test error")

    # Call function
    result = await send_file(mock_ptb_bot, chat_id, tmp_file)

    # Verify that the logger was called
    logot.assert_logged(logged.error("Failed to send file"))
    assert result is None


@pytest.mark.asyncio
async def test_send_file_with_invalid_path(logot: Logot, mock_ptb_bot):
    """Test that send_file handles invalid Path content."""
    chat_id = 123456
    invalid_path = Path("invalid/path/to/file.txt")

    # Call function
    result = await send_file(mock_ptb_bot, chat_id, invalid_path)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("File does not exist"))
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_file_with_directory_path(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles directory Path content."""
    chat_id = 123456

    # Call function
    result = await send_file(mock_ptb_bot, chat_id, tmp_path)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("Path is not a file"))
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_file_with_no_read_permission(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles file with no read permission."""
    chat_id = 123456
    no_permission_file = tmp_path / "no_permission_file.txt"
    no_permission_file.write_text("This file has no read permission.")

    # Remove read permissions
    no_permission_file.chmod(0o000)

    # Call function
    result = await send_file(mock_ptb_bot, chat_id, no_permission_file)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error("No read permission for file"))
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_file_with_empty_file(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles empty file content."""
    chat_id = 123456
    empty_file = tmp_path / "empty_file.txt"
    empty_file.write_text("")

    # Call function
    await send_file(mock_ptb_bot, chat_id, empty_file)

    # Verify that the logger was called with a warning
    logot.assert_logged(logged.warning("File is empty"))
    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=chat_id,
        document=empty_file,
        filename=empty_file.name,
        reply_to_message_id=None,
    )
    logot.assert_logged(logged.debug("File sent"))


@pytest.mark.asyncio
async def test_send_file_too_big(logot: Logot, mock_ptb_bot, tmp_path):
    """Test that send_file handles files that are too big."""
    chat_id = 123456
    big_file = tmp_path / "big_file.txt"
    big_file.write_text("A" * (FileSizeLimit.FILESIZE_UPLOAD + 1))

    assert big_file.stat().st_size > FileSizeLimit.FILESIZE_UPLOAD

    # Call function
    result = await send_file(mock_ptb_bot, chat_id, big_file)

    # Verify that the logger was called with an error
    logot.assert_logged(
        logged.error(
            f"File size ({big_file.stat().st_size} bytes) exceeds Telegram limit of {FileSizeLimit.FILESIZE_UPLOAD} bytes"
        )
    )
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_with_text_content(mock_ptb_bot):
    """Test that send correctly dispatches text content to send_text."""
    chat_id = 123456
    text_content = "Test message"
    reply_to = 789

    with patch("kamihi.tg.send.send_text") as mock_send_text:
        mock_message = Mock(spec=Message)
        mock_send_text.return_value = mock_message

        # Call function
        result = await send(mock_ptb_bot, chat_id, text_content, reply_to)

        # Verify send_text was called with correct parameters
        mock_send_text.assert_called_once_with(mock_ptb_bot, chat_id, text_content, reply_to)
        assert result == mock_message


@pytest.mark.asyncio
async def test_send_with_file_content(mock_ptb_bot, tmp_file):
    """Test that send correctly dispatches Path content to send_file."""
    chat_id = 123456
    reply_to = 789

    with patch("kamihi.tg.send.send_file") as mock_send_file:
        mock_message = Mock(spec=Message)
        mock_send_file.return_value = mock_message

        # Call function
        result = await send(mock_ptb_bot, chat_id, tmp_file, reply_to)

        # Verify send_file was called with correct parameters
        mock_send_file.assert_called_once_with(mock_ptb_bot, chat_id, tmp_file, reply_to)
        assert result == mock_message


@pytest.mark.asyncio
async def test_send_with_unsupported_content(logot: Logot, mock_ptb_bot):
    """Test that send handles unsupported content types correctly."""
    chat_id = 123456
    unsupported_content = 12345  # int is not supported

    result = await send(mock_ptb_bot, chat_id, unsupported_content)

    # Verify that the logger was called with an error
    logot.assert_logged(logged.error(f"Unsupported content type: {type(unsupported_content)}"))
    # Verify function returns None
    assert result is None


@pytest.mark.asyncio
async def test_send_without_reply_to_message_id(mock_ptb_bot):
    """Test that send works correctly when reply_to_message_id is not provided."""
    chat_id = 123456
    text_content = "Test message"

    with patch("kamihi.tg.send.send_text") as mock_send_text:
        mock_message = Mock(spec=Message)
        mock_send_text.return_value = mock_message

        # Call function without reply_to_message_id
        result = await send(mock_ptb_bot, chat_id, text_content)

        # Verify send_text was called with None for reply_to_message_id
        mock_send_text.assert_called_once_with(mock_ptb_bot, chat_id, text_content, None)
        assert result == mock_message


@pytest.mark.asyncio
async def test_reply_with_text_content(mock_update_context):
    """Test that reply correctly handles text content."""
    update, context = mock_update_context
    text_content = "Reply message"

    with patch("kamihi.tg.send.send") as mock_send:
        mock_message = Mock(spec=Message)
        mock_send.return_value = mock_message

        # Call function
        result = await reply(update, context, text_content)

        # Verify send was called with correct parameters
        mock_send.assert_called_once_with(
            context.bot,
            update.effective_message.chat_id,
            text_content,
            reply_to_message_id=update.effective_message.message_id,
        )
        assert result == mock_message


@pytest.mark.asyncio
async def test_reply_with_file_content(mock_update_context, tmp_file):
    """Test that reply correctly handles file content."""
    update, context = mock_update_context

    with patch("kamihi.tg.send.send") as mock_send:
        mock_message = Mock(spec=Message)
        mock_send.return_value = mock_message

        # Call function
        result = await reply(update, context, tmp_file)

        # Verify send was called with correct parameters
        mock_send.assert_called_once_with(
            context.bot,
            update.effective_message.chat_id,
            tmp_file,
            reply_to_message_id=update.effective_message.message_id,
        )
        assert result == mock_message


@pytest.mark.asyncio
async def test_reply_extracts_correct_parameters(mock_update_context):
    """Test that reply correctly extracts parameters from Update and CallbackContext."""
    update, context = mock_update_context
    text_content = "Test reply"

    # Modify the mock to have specific values
    update.effective_message.chat_id = 999888
    update.effective_message.message_id = 777666

    with patch("kamihi.tg.send.send") as mock_send:
        # Call function
        await reply(update, context, text_content)

        # Verify the correct parameters were extracted and passed
        mock_send.assert_called_once_with(
            context.bot,
            999888,  # chat_id
            text_content,
            reply_to_message_id=777666,  # message_id
        )


@pytest.mark.asyncio
async def test_reply_forwards_return_value(mock_update_context):
    """Test that reply correctly forwards the return value from send."""
    update, context = mock_update_context
    text_content = "Test message"

    with patch("kamihi.tg.send.send") as mock_send:
        # Test with successful message
        mock_message = Mock(spec=Message)
        mock_send.return_value = mock_message
        result = await reply(update, context, text_content)
        assert result == mock_message

        # Test with None return (error case)
        mock_send.return_value = None
        result = await reply(update, context, text_content)
        assert result is None
