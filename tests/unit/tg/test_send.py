"""
Tests for the kamihi.tg.send module.

This module contains unit tests for the send_text and reply_text functions
used to send messages via the Telegram API.

License:
    MIT
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Bot, Message
from telegram.error import TelegramError
from telegramify_markdown import markdownify as md

from kamihi.tg.send import reply_text, send_text


@pytest.fixture
def mock_ptb_bot():
    """Fixture to provide a mock Bot instance."""
    bot = Mock(spec=Bot)
    bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    return bot


@pytest.mark.asyncio
async def test_send_text_basic(mock_ptb_bot):
    """
    Test basic functionality of send_text with minimal parameters.

    Validates foundation for markdown-renderizado by ensuring text is sent correctly.
    """
    # Configure return value for send_message
    mock_message = Mock(spec=Message)
    mock_ptb_bot.send_message.return_value = mock_message

    chat_id = 123456
    text = "Test message"

    # Call function
    await send_text(mock_ptb_bot, chat_id, text)

    # Verify send_message was called with correct parameters
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(text), reply_to_message_id=None)


@pytest.mark.asyncio
async def test_send_text_with_reply(mock_ptb_bot):
    """
    Test that send_text correctly handles reply_to_message_id parameter.

    Validates support for proper command response flow in acciones-comandos-reconocimiento.
    """
    chat_id = 123456
    text = "Reply message"
    reply_to = 789

    # Call function
    await send_text(mock_ptb_bot, chat_id, text, reply_to)

    # Verify send_message was called with reply_to_message_id parameter set to reply_to
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(text), reply_to_message_id=reply_to)


@pytest.mark.asyncio
async def test_send_text_with_markdown_formatting(mock_ptb_bot):
    """
    Test that send_text correctly sends messages with Markdown formatting.

    Validates:
    - markdown-procesamiento: "Cuando un usuario envía un mensaje con formato Markdown,
      el sistema procesa correctamente las etiquetas de formato."
    - markdown-renderizado: "Cuando un desarrollador implementa una acción que genera
      texto con formato Markdown, el sistema renderiza correctamente todas las etiquetas de formato."
    """
    chat_id = 123456
    markdown_text = "*Bold text* and _italic text_"

    # Call function
    await send_text(mock_ptb_bot, chat_id, markdown_text)

    # Verify markdown text is preserved when sending
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(markdown_text), reply_to_message_id=None)


@pytest.mark.asyncio
async def test_send_text_with_special_markdown_characters(mock_ptb_bot):
    """
    Test that send_text correctly handles special Markdown characters.

    Validates:
    - markdown-caracteres: "Cuando se utilizan caracteres especiales junto con etiquetas de formato,
      el sistema escapa correctamente los caracteres para evitar conflictos con la sintaxis de Markdown."
    """
    chat_id = 123456
    text_with_special_chars = "Special characters: *asterisks*, _underscores_, `backticks`"

    # Call function
    await send_text(mock_ptb_bot, chat_id, text_with_special_chars)

    # Verify text with special characters is sent correctly
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(text_with_special_chars), reply_to_message_id=None)


@pytest.mark.asyncio
async def test_send_text_with_complex_markdown(mock_ptb_bot):
    """
    Test that send_text correctly handles complex Markdown formatting.

    Validates:
    - markdown-combinacion: "Al combinar múltiples estilos de formato en un mismo mensaje,
      el sistema mantiene la jerarquía correcta del formato."
    """
    chat_id = 123456
    complex_markdown = "_*Bold inside italic*_ and *_Italic inside bold_*."

    # Call function
    await send_text(mock_ptb_bot, chat_id, complex_markdown)

    # Verify complex markdown is preserved
    mock_ptb_bot.send_message.assert_called_once_with(chat_id, md(complex_markdown), reply_to_message_id=None)


@pytest.mark.asyncio
async def test_send_text_error_handling(mock_ptb_bot):
    """
    Test that send_text properly catches and logs TelegramError.

    Validates supports markdown-errores by ensuring errors in message sending are properly handled.
    """
    chat_id = 123456
    text = "Test message"

    # Make send_message raise a TelegramError
    mock_ptb_bot.send_message.side_effect = TelegramError("Test error")

    # We need to patch the logger in a way that prevents the exception from propagating
    with patch("kamihi.tg.send.logger") as mock_logger:
        # Set up the chained mocks correctly
        mock_bind = Mock()
        mock_logger.bind.return_value = mock_bind

        # Create a context manager that will swallow the exception
        class MockCatch:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                # Return True to indicate the exception was handled
                return True

        mock_bind.catch.return_value = MockCatch()

        # Call the function (should not raise now because context manager swallows exception)
        result = await send_text(mock_ptb_bot, chat_id, text)

        # Verify bind was called with correct parameters
        mock_logger.bind.assert_called_once()
        # Verify catch was called with the correct arguments
        mock_bind.catch.assert_called_once_with(exception=TelegramError, message="Failed to send message")
        # Verify the function returned None (since there was an error)
        assert result is None


@pytest.mark.asyncio
async def test_send_text_handles_markdown_errors(mock_ptb_bot):
    """
    Test that send_text properly handles malformed Markdown content.

    Validates:
    - markdown-errores: "Al utilizar etiquetas de Markdown inválidas o mal formadas,
      el sistema detecta los errores y muestra un mensaje informativo sobre el formato correcto."
    """
    chat_id = 123456
    malformed_markdown = "This has *unclosed bold"

    # Make send_message raise a TelegramError for malformed markdown
    error = TelegramError("Bad markdown formatting")
    mock_ptb_bot.send_message.side_effect = error

    # We need to patch the logger in a way that prevents the exception from propagating
    with patch("kamihi.tg.send.logger") as mock_logger:
        # Set up the chained mocks correctly
        mock_bind = Mock()
        mock_logger.bind.return_value = mock_bind

        # Create a context manager that will swallow the exception
        class MockCatch:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                # Return True to indicate the exception was handled
                return True

        mock_bind.catch.return_value = MockCatch()

        # Call the function (should not raise now)
        result = await send_text(mock_ptb_bot, chat_id, malformed_markdown)

        # Verify bind was called with the right parameters
        mock_logger.bind.assert_called_with(chat_id=chat_id, received_id=None, response_text=malformed_markdown)
        # Verify catch was called with the correct arguments
        mock_bind.catch.assert_called_with(exception=TelegramError, message="Failed to send message")
        # Verify function returns None on error
        assert result is None


@pytest.mark.asyncio
async def test_reply_text(mock_update, mock_context):
    """
    Test that reply_text correctly extracts parameters and calls send_text.

    Validates support for proper command response flow in acciones-comandos-reconocimiento.
    """
    text = "Reply message"

    # Patch send_text to verify it gets called with correct parameters
    with patch("kamihi.tg.send.send_text", new=AsyncMock()) as mock_send_text:
        # Call function
        await reply_text(mock_update, mock_context, text)

        # Verify send_text was called with parameters extracted from update and context
        mock_send_text.assert_called_once_with(
            mock_context.bot, mock_update.effective_message.chat_id, text, mock_update.effective_message.message_id
        )
