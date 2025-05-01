"""
Tests for the kamihi.tg.default_handlers module.

This module contains unit tests for the default and error handlers
used by the Telegram bot.

License:
    MIT
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Update
from telegram.ext import CallbackContext

from kamihi.tg.default_handlers import default, error


@pytest.fixture
def mock_update():
    """Fixture to provide a mock Update instance."""
    update = Mock(spec=Update)
    update.effective_message = Mock()
    update.effective_message.chat_id = 123456
    update.effective_message.message_id = 789
    return update


@pytest.fixture
def mock_context():
    """Fixture to provide a mock CallbackContext."""
    context = Mock(spec=CallbackContext)
    context.bot_data = {"responses": {"default_message": "Default response", "error_message": "Error occurred"}}
    return context


@pytest.mark.asyncio
async def test_default_handler(mock_update, mock_context):
    """
    Test that the default handler calls reply_text with the correct message.

    Validates supports acciones-comandos-formato indirectly by ensuring
    users receive appropriate responses when commands aren't recognized.
    """
    # Patch reply_text to verify it's called with the right parameters
    with patch("kamihi.tg.default_handlers.reply_text", new=AsyncMock()) as mock_reply:
        # Call the default handler
        await default(mock_update, mock_context)

        # Verify reply_text is called with the correct text from bot_data
        mock_reply.assert_called_once_with(
            mock_update, mock_context, mock_context.bot_data["responses"]["default_message"]
        )


@pytest.mark.asyncio
async def test_default_handler_logging(mock_update, mock_context):
    """
    Test that the default handler logs the message correctly.

    Validates system diagnostic functionality that supports proper
    operation of acciones-comandos-reconocimiento.
    """
    # Patch reply_text to avoid actually calling it
    with patch("kamihi.tg.default_handlers.reply_text", new=AsyncMock()):
        # Patch logger to verify logging behavior
        with patch("kamihi.tg.default_handlers.logger") as mock_logger:
            # Set up bind return value to enable method chaining
            bind_mock = Mock()
            mock_logger.bind.return_value = bind_mock

            # Call the default handler
            await default(mock_update, mock_context)

            # Verify logger.bind is called with chat_id and message_id
            mock_logger.bind.assert_called_once_with(
                chat_id=mock_update.effective_message.chat_id, message_id=mock_update.effective_message.message_id
            )

            # Verify debug log is called with the correct message
            bind_mock.debug.assert_called_once_with(
                "Received message but no handler matched, so sending default response"
            )


@pytest.mark.asyncio
async def test_error_handler_with_update(mock_update, mock_context):
    """
    Test error handler behavior when an update is available.

    Validates supports acciones-comandos-formato by ensuring users
    receive appropriate error messages.
    """
    # Set up an error in the context
    test_error = Exception("Test error")
    mock_context.error = test_error

    # Patch reply_text to verify it gets called
    with patch("kamihi.tg.default_handlers.reply_text", new=AsyncMock()) as mock_reply:
        # Call the error handler with a valid update
        await error(mock_update, mock_context)

        # Verify reply_text is called with the error text
        mock_reply.assert_called_once_with(
            mock_update, mock_context, mock_context.bot_data["responses"]["error_message"]
        )


@pytest.mark.asyncio
async def test_error_handler_no_update():
    """
    Test error handler behavior when no update is available.

    Validates system robustness that supports acciones-comandos-concurrencia
    by ensuring errors don't crash the system.
    """
    # Create a context with an error, but no update
    mock_context = Mock(spec=CallbackContext)
    mock_context.error = Exception("Test error")
    mock_context.bot_data = {"responses": {"error_text": "Error occurred"}}

    # Patch reply_text to verify it's NOT called when there's no update
    with patch("kamihi.tg.default_handlers.reply_text", new=AsyncMock()) as mock_reply:
        # Call the error handler with no update (None)
        await error(None, mock_context)

        # Verify reply_text is NOT called (since update is None)
        mock_reply.assert_not_called()


@pytest.mark.asyncio
async def test_error_handler_logging():
    """
    Test that the error handler properly logs the exception.

    Validates system diagnostic functionality that supports proper
    operation of all error handling.
    """
    # Create context with a test error
    mock_context = Mock(spec=CallbackContext)
    test_error = Exception("Test error")
    mock_context.error = test_error

    # Patch logger to verify logging behavior
    with patch("kamihi.tg.default_handlers.logger") as mock_logger:
        # Set up opt return value
        opt_mock = Mock()
        mock_logger.opt.return_value = opt_mock

        # Call the error handler
        await error(None, mock_context)

        # Verify logger.opt is called with the exception
        mock_logger.opt.assert_called_once_with(exception=test_error)

        # Verify error log is called with the correct message
        opt_mock.error.assert_called_once_with("An error occurred")
