"""
Tests for the kamihi.tg.default_handlers module.

This module contains unit tests for the default and error handlers
used by the Telegram bot.

License:
    MIT
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from logot import Logot, logged
from telegram import Update
from telegram.ext import CallbackContext, ApplicationHandlerStop

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
    """Test that the default handler calls reply with the correct message."""
    # Patch reply to verify it's called with the right parameters
    with (
        patch("kamihi.tg.default_handlers.send", new=AsyncMock()) as mock_reply,
        pytest.raises(ApplicationHandlerStop),
    ):
        # Call the default handler
        await default(mock_update, mock_context)

        # Verify reply is called with the correct text from bot_data
        mock_reply.assert_called_once_with(
            mock_context.bot_data["responses"]["default_message"], update=mock_update, context=mock_context
        )


@pytest.mark.asyncio
async def test_default_handler_logging(logot: Logot, mock_update, mock_context):
    """Test that the default handler logs the message correctly."""
    # Patch reply to avoid actually calling it
    with (
        patch("kamihi.tg.default_handlers.send", new=AsyncMock()) as mock_reply,
        pytest.raises(ApplicationHandlerStop),
    ):
        # Call the default handler
        await default(mock_update, mock_context)

        # Verify reply is called
        logot.assert_logged(logged.debug("Received message but no handler matched, so sending default response"))

        # Verify reply is called with the correct text
        mock_reply.assert_called_once_with(
            mock_context.bot_data["responses"]["default_message"], update=mock_update, context=mock_context
        )


@pytest.mark.asyncio
async def test_error_handler_update(logot: Logot, mock_update, mock_context):
    """Test error handler behavior when an update is available."""
    # Set up an error in the context
    test_error = Exception("Test error")
    mock_context.error = test_error

    # Patch reply to verify it gets called
    with (
        patch("kamihi.tg.default_handlers.send", new=AsyncMock()) as mock_reply,
        pytest.raises(ApplicationHandlerStop),
    ):
        # Call the error handler with a valid update
        await error(mock_update, mock_context)

        # Verify that the logger is called with the error
        logot.assert_logged(logged.error("An error occurred"))

        # Verify reply is called with the error text
        mock_reply.assert_called_once_with(
            mock_context.bot_data["responses"]["default_message"], update=mock_update, context=mock_context
        )


@pytest.mark.asyncio
async def test_error_handler_no_update(logot: Logot):
    """Test error handler behavior when no update is available."""
    # Create a context with an error, but no update
    mock_context = Mock(spec=CallbackContext)
    mock_context.error = Exception("Test error")

    # Patch reply to verify it's NOT called when there's no update
    with (
        patch("kamihi.tg.default_handlers.send", new=AsyncMock()) as mock_reply,
        pytest.raises(ApplicationHandlerStop),
    ):
        # Call the error handler with no update (None)
        await error(None, mock_context)

        # Verify that the logger is called with the error
        logot.assert_logged(logged.error("An error occurred"))

        # Verify reply is NOT called (since update is None)
        mock_reply.assert_not_called()
