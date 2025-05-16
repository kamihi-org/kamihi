"""
Tests for the kamihi.tg.client module.

This module contains unit tests for the TelegramClient class
and related functions in the kamihi.tg.client module.

License:
    MIT
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import Application, ApplicationBuilder, BaseHandler

from kamihi.base.config import KamihiSettings
from kamihi.tg.client import TelegramClient, _post_init, _post_shutdown


@pytest.fixture
def mock_app():
    """Create a mock Application instance."""
    app = Mock(spec=Application)
    app.add_handler = Mock()
    app.add_error_handler = Mock()
    app.run_polling = Mock()
    app.stop = AsyncMock()
    return app


@pytest.fixture
def mock_builder():
    """Create a mock ApplicationBuilder instance."""
    builder = Mock(spec=ApplicationBuilder)
    builder.token.return_value = builder
    builder.defaults.return_value = builder
    builder.post_init.return_value = builder
    builder.post_shutdown.return_value = builder
    builder.persistence.return_value = builder
    return builder


@pytest.fixture
def mock_settings():
    """Create a mock KamihiSettings instance."""
    settings = Mock(spec=KamihiSettings)
    settings.token = "test_token"
    settings.timezone_obj = None
    settings.testing = True
    settings.model_dump_json.return_value = "{}"

    # Create a nested mock for responses
    responses_mock = Mock()
    responses_mock.default_enabled = True
    settings.responses = responses_mock

    return settings


@pytest.fixture
def client(mock_builder, mock_app):
    """Create a TelegramClient instance with mocked dependencies."""
    with patch("kamihi.tg.client.Application.builder", return_value=mock_builder):
        mock_builder.build.return_value = mock_app
        settings = Mock(spec=KamihiSettings)
        settings.token = "test_token"
        settings.timezone_obj = None
        settings.testing = True
        settings.model_dump_json.return_value = "{}"

        # Create a nested mock for responses
        responses_mock = Mock()
        responses_mock.default_enabled = True
        settings.responses = responses_mock

        client = TelegramClient(settings, [])
        return client


@pytest.mark.asyncio
async def test_post_init():
    """
    Test that _post_init logs a success message.

    Validates core functionality that supports acciones-creacion-actualizacion
    by ensuring proper initialization.
    """
    mock_app = Mock()

    with patch("kamihi.tg.client.logger.success") as mock_logger:
        await _post_init(mock_app)
        mock_logger.assert_called_once_with("Started!")


@pytest.mark.asyncio
async def test_post_shutdown():
    """
    Test that _post_shutdown logs a success message.

    Validates core functionality that supports acciones-creacion-actualizacion
    by ensuring proper shutdown.
    """
    mock_app = Mock()

    with patch("kamihi.tg.client.logger.success") as mock_logger:
        await _post_shutdown(mock_app)
        mock_logger.assert_called_once_with("Stopped!")


def test_run_calls_run_polling(client, mock_app):
    """
    Test that run method calls _app.run_polling with correct parameters.

    Validates core functionality that supports acciones-creacion-alta and
    acciones-creacion-reconocimiento by ensuring the bot can start correctly.
    """
    client.run()
    mock_app.run_polling.assert_called_once_with(allowed_updates=Update.ALL_TYPES)


@pytest.mark.asyncio
async def test_stop_calls_stop(client, mock_app):
    """
    Test that stop method calls _app.stop.

    Validates core functionality that supports acciones-creacion-actualizacion
    by ensuring proper shutdown.
    """
    await client.stop()
    mock_app.stop.assert_called_once()


def test_handler_registration(mock_settings, mock_builder, mock_app):
    """
    Test that handlers are properly registered with the application.

    Verifies that each handler in the provided list is correctly added to the application.
    """
    # Create mock handlers
    mock_handler1 = Mock(spec=BaseHandler)
    mock_handler2 = Mock(spec=BaseHandler)
    handlers = [mock_handler1, mock_handler2]

    # Set up the application builder mock
    with patch("kamihi.tg.client.Application.builder", return_value=mock_builder):
        mock_builder.build.return_value = mock_app

        # Create the client with mock handlers
        TelegramClient(mock_settings, handlers)

        # Verify that add_handler was called for each handler
        assert mock_app.add_handler.call_count == 3  # 2 handlers + 1 default handler
        mock_app.add_handler.assert_any_call(mock_handler1)
        mock_app.add_handler.assert_any_call(mock_handler2)


def test_handler_registration_with_error(mock_settings, mock_builder, mock_app):
    """
    Test handler registration when a TelegramError occurs.

    Verifies that when add_handler raises a TelegramError for one handler,
    the error is caught and registration continues with the next handler.
    """
    # Create mock handlers
    mock_handler1 = Mock(spec=BaseHandler)
    mock_handler2 = Mock(spec=BaseHandler)
    handlers = [mock_handler1, mock_handler2]

    # Set up the application builder mock
    with patch("kamihi.tg.client.Application.builder", return_value=mock_builder):
        mock_builder.build.return_value = mock_app

        # Make add_handler raise a TelegramError for the first handler
        def add_handler_side_effect(handler, group=None):
            if handler == mock_handler1:
                raise TelegramError("Test error")

        mock_app.add_handler.side_effect = add_handler_side_effect

        # Create the client - this should not raise an exception due to logger.catch
        TelegramClient(mock_settings, handlers)

        # Verify that add_handler was called for both handlers
        assert mock_app.add_handler.call_count == 3  # 2 handlers + 1 default handler
