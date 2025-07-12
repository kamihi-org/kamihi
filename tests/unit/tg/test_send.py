"""
Tests for the kamihi.tg.send module.

This module contains unit tests for the send_text, send_file, send, and reply functions
used to send messages via the Telegram API.

License:
    MIT
"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from logot import Logot, logged
from telegram import Bot, Message, Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

from kamihi.tg.media import Audio, Document, Photo, Video, Voice, Media
from kamihi.tg.send import send


@pytest.fixture
def mock_ptb_bot():
    """Fixture to provide a mock Bot instance."""
    bot = Mock(spec=Bot)
    bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    bot.send_document = AsyncMock(return_value=Mock(spec=Message))
    bot.send_photo = AsyncMock(return_value=Mock(spec=Message))
    bot.send_video = AsyncMock(return_value=Mock(spec=Message))
    bot.send_audio = AsyncMock(return_value=Mock(spec=Message))
    bot.send_voice = AsyncMock(return_value=Mock(spec=Message))
    bot.send_location = AsyncMock(return_value=Mock(spec=Message))
    bot.send_media_group = AsyncMock(return_value=[Mock(spec=Message)])
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
        filename=tmp_image_file.name,
        caption=None,
        photo=tmp_image_file,
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
        filename=tmp_video_file.name,
        caption=None,
        video=tmp_video_file,
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
        filename=tmp_audio_file.name,
        caption=None,
        audio=tmp_audio_file,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as audio"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_voice(logot: Logot, tmp_voice_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending a voice note file using just the path."""
    # Call function
    result = await send(tmp_voice_file, update=mock_update, context=mock_context)

    # Verify send_voice was called with correct parameters
    mock_ptb_bot.send_voice.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        filename=tmp_voice_file.name,
        caption=None,
        voice=tmp_voice_file,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as voice note"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_document(logot: Logot, tmp_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending a file using just the path."""
    # Call function
    result = await send(tmp_file, update=mock_update, context=mock_context)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        filename=tmp_file.name,
        caption=None,
        document=tmp_file,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as generic file"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_media_group(
    logot: Logot, tmp_image_file, tmp_video_file, mock_ptb_bot, mock_update, mock_context
):
    """Test sending a media group using paths."""
    # Call function
    result = await send([tmp_image_file, tmp_video_file], update=mock_update, context=mock_context)

    # Verify send_media_group was called with correct parameters
    mock_ptb_bot.send_media_group.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        media=[
            Photo(tmp_image_file).as_input_media(),
            Video(tmp_video_file).as_input_media(),
        ],
    )
    assert result is not None
    logot.assert_logged(
        logged.debug("Received list of file paths, guessing media types and trying to send as media group")
    )
    logot.assert_logged(logged.debug("Sending as media group"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_path_invalid(logot: Logot, mock_ptb_bot, mock_update, mock_context):
    """Test sending an invalid Path."""
    invalid_path = Path("invalid/path/to/file.txt")

    # Call function
    with pytest.raises(FileNotFoundError):
        await send(invalid_path, update=mock_update, context=mock_context)


@pytest.mark.asyncio
async def test_send_bytes(logot: Logot, tmp_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending a bytes object."""
    # Call function
    result = await send(tmp_file.read_bytes(), update=mock_update, context=mock_context)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        filename=None,
        document=tmp_file.read_bytes(),
        caption=None,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as generic file"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_io(logot: Logot, tmp_file, mock_ptb_bot, mock_update, mock_context):
    """Test sending an IO object."""
    # Create the IO object
    tmp_file = tmp_file.open("rb")

    # Call function
    result = await send(tmp_file, update=mock_update, context=mock_context)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        filename=None,
        caption=None,
        document=tmp_file,
    )
    assert result is not None
    logot.assert_logged(logged.debug("Sending as generic file"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", [None, md("Test caption")])
async def test_send_media_document(logot: Logot, tmp_file, caption, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_file with minimal parameters."""
    # Call function
    await send(Document(tmp_file, caption=caption), update=mock_update, context=mock_context)

    # Verify send_document was called with correct parameters
    mock_ptb_bot.send_document.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        filename=tmp_file.name,
        document=tmp_file,
        caption=md(caption) if caption else None,
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
        filename=tmp_image_file.name,
        photo=tmp_image_file,
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
        filename=tmp_video_file.name,
        video=tmp_video_file,
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
        filename=tmp_audio_file.name,
        audio=tmp_audio_file,
        caption=caption,
    )
    logot.assert_logged(logged.debug("Sending as audio"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", [None, md("Test caption")])
async def test_send_media_voice(logot: Logot, tmp_voice_file, caption, mock_ptb_bot, mock_update, mock_context):
    """Test basic functionality of send_voice with minimal parameters."""
    # Call function
    await send(Voice(tmp_voice_file, caption=caption), update=mock_update, context=mock_context)

    # Verify send_voice was called with correct parameters
    mock_ptb_bot.send_voice.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        filename=tmp_voice_file.name,
        voice=tmp_voice_file,
        caption=caption,
    )
    logot.assert_logged(logged.debug("Sending as voice note"))
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
        horizontal_accuracy=location.horizontal_accuracy,
    )
    logot.assert_logged(logged.debug("Sending as location"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_media_group(logot: Logot, tmp_image_file, tmp_video_file, mock_update, mock_context):
    """Test sending a media group with mixed media types."""
    items = [Photo(tmp_image_file), Video(tmp_video_file)]

    # Call function
    results = await send(items, update=mock_update, context=mock_context)

    # Verify that send_media_group was called with correct parameters
    assert len(results) == 1
    mock_context.bot.send_media_group.assert_called_with(
        chat_id=mock_update.effective_chat.id,
        media=[
            Photo(tmp_image_file).as_input_media(),
            Video(tmp_video_file).as_input_media(),
        ],
    )
    logot.assert_logged(logged.debug("Sending as media group"))
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
        filename=tmp_file.name,
        caption=None,
        document=tmp_file,
    )
    mock_context.bot.send_photo.assert_called_with(
        chat_id=mock_update.effective_chat.id,
        filename=tmp_image_file.name,
        caption=md("Test caption"),
        photo=tmp_image_file,
    )
    mock_context.bot.send_message.assert_called_with(
        chat_id=mock_update.effective_chat.id,
        text=md("Test message"),
    )
    logot.assert_logged(logged.debug("Sending as list of items"))
    logot.assert_logged(logged.debug("Sent"))


@pytest.mark.asyncio
async def test_send_invalid_type(mock_update, mock_context):
    """Test sending an unsupported object type."""
    invalid_obj = object()

    # Call function
    with pytest.raises(TypeError, match=f"Object of type {type(invalid_obj)} cannot be sent"):
        await send(invalid_obj, update=mock_update, context=mock_context)


@pytest.mark.asyncio
async def test_send_invalid_media_type(mock_update, mock_context, tmp_file):
    """Test sending an unsupported object type."""

    class InvalidMedia(Media):
        """An invalid media type for testing."""

    # Call function
    with pytest.raises(TypeError, match=f"Object of type {InvalidMedia} cannot be sent"):
        await send(InvalidMedia(tmp_file), update=mock_update, context=mock_context)
