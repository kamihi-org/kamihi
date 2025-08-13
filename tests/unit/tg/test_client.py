"""
Tests for the kamihi.tg.client module.

This module contains unit tests for the TelegramClient class
and related functions in the kamihi.tg.client module.

License:
    MIT
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from logot import Logot, logged
from telegram import Update, Bot, BotCommand, BotCommandScopeChat
from telegram.error import TelegramError
from telegram.ext import Application, ApplicationBuilder, BaseHandler

from kamihi.base.config import KamihiSettings
from kamihi.tg.client import TelegramClient


@pytest.fixture
def mock_app():
    """Create a mock Application instance."""
    app = Mock(spec=Application)
    app.add_handler = Mock()
    app.add_error_handler = Mock()
    app.run_polling = Mock()
    app.stop = AsyncMock()
    app.bot = Mock(spec=Bot)
    app.bot.delete_my_commands = AsyncMock()
    app.bot.set_my_commands = AsyncMock()

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
    settings.testing = False
    settings.model_dump_json.return_value = "{}"

    # Create a nested mock for responses
    responses_mock = Mock()
    responses_mock.default_enabled = True
    settings.responses = responses_mock

    return settings


@pytest.fixture
def client(mock_builder, mock_settings, mock_app):
    """Create a TelegramClient instance with mocked dependencies."""
    with patch("kamihi.tg.client.Application.builder", return_value=mock_builder):
        mock_builder.build.return_value = mock_app

        client = TelegramClient(mock_settings, [], lambda: None, lambda: None)
        return client


@pytest.fixture
def client_testing(mock_builder, mock_settings, mock_app):
    """Create a TelegramClient instance with mocked dependencies."""
    with patch("kamihi.tg.client.Application.builder", return_value=mock_builder):
        mock_builder.build.return_value = mock_app
        mock_settings.testing = True

        client = TelegramClient(mock_settings, [], lambda: None, lambda: None)
        return client


def test_init(client, mock_settings):
    """Test that TelegramClient initializes correctly."""
    assert client._bot_settings == mock_settings
    assert client._app is not None


def test_init_testing_mode(client_testing, mock_settings):
    """Test that TelegramClient initializes correctly in testing mode."""
    assert client_testing._bot_settings == mock_settings
    assert client_testing._app is not None
    assert client_testing._base_url == "https://api.telegram.org/bot{token}/test"


def test_init_register_handler_error(mock_settings, mock_builder, mock_app, logot: Logot):
    """Test that TelegramClient handles errors during handler registration."""
    # Create a mock handler
    mock_handler = Mock(spec=BaseHandler)

    # Set up the application builder mock
    with patch("kamihi.tg.client.Application.builder", return_value=mock_builder):
        mock_builder.build.return_value = mock_app

        # Make add_handler raise a TelegramError
        mock_app.add_handler.side_effect = TelegramError("Test error")

        # Create the client - this should not raise an exception due to logger.catch
        TelegramClient(mock_settings, [mock_handler], lambda: None, lambda: None)

        logot.assert_logged(logged.error("Failed to register handler"))
        logot.assert_logged(logged.error("Failed to register default handlers"))


@pytest.mark.asyncio
async def test_reset_scopes(client, mock_app):
    """Test that reset_scopes method calls _app.reset_scopes."""
    await client.reset_scopes()
    mock_app.bot.delete_my_commands.assert_called_once()


@pytest.mark.asyncio
async def test_reset_scopes_testing_mode(client_testing, mock_app, logot: Logot):
    """Test that reset_scopes does not call _app.reset_scopes in testing mode."""
    await client_testing.reset_scopes()
    mock_app.bot.delete_my_commands.assert_not_called()
    logot.assert_logged(logged.debug("Testing mode, skipping resetting scopes"))


@pytest.mark.asyncio
async def test_reset_scopes_telegram_error(client, mock_app, logot: Logot):
    """Test that reset_scopes handles TelegramError during command deletion."""
    mock_app.bot.delete_my_commands.side_effect = TelegramError("Test error")

    await client.reset_scopes()

    mock_app.bot.delete_my_commands.assert_called_once()
    logot.assert_logged(logged.error("Failed to reset scopes"))


@pytest.mark.asyncio
async def test_set_scopes(client, mock_app, logot: Logot):
    """Test that set_scopes method calls _app.bot.set_my_commands."""
    await client.set_scopes({123456789: [BotCommand("test", "Test command")]})
    mock_app.bot.set_my_commands.assert_called_once_with(
        commands=[BotCommand("test", "Test command")],
        scope=BotCommandScopeChat(123456789),
    )
    logot.assert_logged(logged.debug("Scopes set"))


@pytest.mark.asyncio
async def test_set_scopes_testing_mode(client_testing, mock_app, logot: Logot):
    """Test that set_scopes does not call _app.bot.set_my_commands in testing mode."""
    await client_testing.set_scopes({123456789: [BotCommand("test", "Test command")]})
    mock_app.bot.set_my_commands.assert_not_called()
    logot.assert_logged(logged.debug("Testing mode, skipping setting scopes"))


@pytest.mark.asyncio
async def test_set_scopes_telegram_error(client, mock_app, logot: Logot):
    """Test that set_scopes handles TelegramError during command setting."""
    mock_app.bot.set_my_commands.side_effect = TelegramError("Test error")

    await client.set_scopes({123456789: [BotCommand("test", "Test command")]})

    mock_app.bot.set_my_commands.assert_called_once_with(
        commands=[BotCommand("test", "Test command")],
        scope=BotCommandScopeChat(123456789),
    )
    logot.assert_logged(logged.error("Failed to set scopes"))


def test_run(client, mock_app, logot: Logot):
    """Test that run method calls _app.run_polling with correct parameters."""
    client.run()
    mock_app.run_polling.assert_called_once_with(allowed_updates=Update.ALL_TYPES)


@pytest.mark.asyncio
async def test_stop(client, mock_app, logot: Logot):
    """Test that stop method calls _app.stop."""
    await client.stop()
    mock_app.stop.assert_called_once()
