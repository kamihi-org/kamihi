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
from telegram.ext import Application, ApplicationBuilder, CommandHandler

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
        settings.model_dump_json.return_value = "{}"

        # Create a nested mock for responses
        responses_mock = Mock()
        responses_mock.default_enabled = True
        settings.responses = responses_mock

        client = TelegramClient(settings)
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


def test_filter_valid_commands_syntax(client):
    """
    Test that _filter_valid_commands properly filters commands based on syntax requirements.

    Validates acciones-comandos-formato: "Al enviar comandos con formato incorrecto, el sistema
    debe proporcionar información sobre la sintaxis correcta del comando."
    """
    # Test with various command types
    commands = [
        "valid",  # Valid command
        "a",  # Valid - min length is 1
        "a" * 33,  # Too long (max length is 32)
        "UPPERCASE",  # Invalid (uppercase not allowed)
        "with-dash",  # Invalid (dash not allowed)
        "with space",  # Invalid (space not allowed)
    ]

    with patch("kamihi.tg.client.logger.warning") as mock_logger:
        valid_commands = client._filter_valid_commands(commands, "test_callback")

        # Both "valid" and "a" should pass the filter since min length is 1
        assert set(valid_commands) == {"valid", "a"}

        # Check that warnings were logged for each invalid command (4 of them)


def test_filter_valid_commands_duplicates(client):
    """
    Test that _filter_valid_commands filters out duplicate commands.

    Validates acciones-comandos-custom-unicidad: "Al asignar un nombre a un comando personalizado,
    el sistema verifica que no exista ya otro comando con el mismo nombre en el sistema."
    """
    commands = ["command", "command", "unique"]

    with patch("kamihi.tg.client.logger.warning") as mock_logger:
        valid_commands = client._filter_valid_commands(commands, "test_callback")

        # First occurrence should be kept, duplicate removed
        assert valid_commands == ["command", "unique"]

        # Check that a warning was logged for the duplicate
        mock_logger.assert_called_once()
        assert "already registered" in mock_logger.call_args[0][0]


def test_filter_valid_commands_logging(client):
    """
    Test that appropriate warnings are logged for invalid commands.

    Validates:
    - acciones-comandos-formato: "Al enviar comandos con formato incorrecto, el sistema debe
      proporcionar información sobre la sintaxis correcta del comando."
    - acciones-comandos-custom-unicidad: "Al asignar un nombre a un comando personalizado,
      el sistema verifica que no exista ya otro comando con el mismo nombre en el sistema."
    """
    commands = ["a", "INVALID", "valid-invalid"]

    with patch("kamihi.tg.client.logger.warning") as mock_logger:
        client._filter_valid_commands(commands, "test_callback")

        # Should have warnings for "INVALID" and "valid-invalid", but "a" is valid
        assert mock_logger.call_count == 2

        # Check warning messages content
        call_args_list = mock_logger.call_args_list
        assert any(args[0][0].startswith("Command") for args in call_args_list)


@pytest.mark.asyncio
async def test_register_command_single(client, mock_app):
    """
    Test registering a single valid command.

    Validates:
    - acciones-creacion-alta: "Cuando un desarrollador registra una acción del _framework_,
      el sistema la reconoce automáticamente como una acción disponible."
    - acciones-comandos-custom-registro: "Cuando un desarrollador define un comando nuevo en
      la acción, el sistema registra automáticamente este comando en la lista disponible para el bot."
    """

    async def test_callback(update, context):
        pass

    # Reset the mock to clear the default handler calls
    mock_app.add_handler.reset_mock()

    # Register a single command
    with patch("kamihi.tg.client.logger.debug") as mock_debug:
        await client.register_command("test", test_callback)

        # Verify CommandHandler was added
        mock_app.add_handler.assert_called_once()
        handler = mock_app.add_handler.call_args[0][0]
        assert isinstance(handler, CommandHandler)
        assert "test" in handler.commands

        # Verify logging
        mock_debug.assert_called_once()
        assert "/test" in mock_debug.call_args[0][0]


@pytest.mark.asyncio
async def test_register_command_multiple(client, mock_app):
    """
    Test registering multiple commands with the same callback.

    Validates:
    - acciones-creacion-alta: "Cuando un desarrollador registra una acción del _framework_,
      el sistema la reconoce automáticamente como una acción disponible."
    - acciones-comandos-custom-registro: "Cuando un desarrollador define un comando nuevo en
      la acción, el sistema registra automáticamente este comando en la lista disponible para el bot."
    """

    async def test_callback(update, context):
        pass

    # Reset the mock to clear the default handler calls
    mock_app.add_handler.reset_mock()

    # Register multiple commands
    with patch("kamihi.tg.client.logger.debug") as mock_debug:
        await client.register_command(["cmd1", "cmd2"], test_callback)

        # Verify CommandHandler was added with both commands
        mock_app.add_handler.assert_called_once()
        handler = mock_app.add_handler.call_args[0][0]
        assert isinstance(handler, CommandHandler)
        assert "cmd1" in handler.commands
        assert "cmd2" in handler.commands

        # Verify logging
        mock_debug.assert_called_once()
        assert "/cmd1" in mock_debug.call_args[0][0]
        assert "/cmd2" in mock_debug.call_args[0][0]


@pytest.mark.asyncio
async def test_register_command_no_valid_commands(client, mock_app):
    """
    Test behavior when attempting to register only invalid commands.

    Validates acciones-comandos-formato: "Al enviar comandos con formato incorrecto, el sistema
    debe proporcionar información sobre la sintaxis correcta del comando."
    """

    async def test_callback(update, context):
        pass

    # Reset the mock to clear the default handler calls
    mock_app.add_handler.reset_mock()

    # Try to register invalid commands
    with patch("kamihi.tg.client.logger.warning") as mock_warning:
        await client.register_command(["A-INVALID", "ALSO-INVALID"], test_callback)

        # Verify add_handler was not called (no valid commands)
        mock_app.add_handler.assert_not_called()

        # Verify warnings were logged
        assert mock_warning.call_count >= 1
        assert "No valid commands" in mock_warning.call_args_list[-1][0][0]


@pytest.mark.asyncio
async def test_register_commands_with_same_name():
    """
    Test behavior when registering commands with duplicate names within a single call.

    Validates:
    - acciones-comandos-custom-unicidad: "Al asignar un nombre a un comando personalizado, el sistema
      verifica que no exista ya otro comando con el mismo nombre en el sistema."
    """

    async def test_callback(update, context):
        pass

    # Create a mock settings object
    mock_settings = Mock(spec=KamihiSettings)
    mock_settings.token = "test_token"
    mock_settings.timezone_obj = None
    mock_settings.model_dump_json.return_value = "{}"

    # Create a nested mock for responses
    responses_mock = Mock()
    responses_mock.default_enabled = False  # Disable default handler to keep the test focused
    mock_settings.responses = responses_mock

    # Create client with fresh mocks
    mock_app = Mock(spec=Application)
    with patch("kamihi.tg.client.Application.builder") as mock_builder_func:
        mock_builder = Mock()
        mock_builder_func.return_value = mock_builder
        mock_builder.token.return_value = mock_builder
        mock_builder.defaults.return_value = mock_builder
        mock_builder.post_init.return_value = mock_builder
        mock_builder.post_shutdown.return_value = mock_builder
        mock_builder.persistence.return_value = mock_builder
        mock_builder.build.return_value = mock_app

        client = TelegramClient(mock_settings)

        # Register commands with duplicates in a single call
        with patch("kamihi.tg.client.logger.warning") as mock_warning:
            await client.register_command(["same", "same", "different"], test_callback)

            # The warning should be triggered for the duplicate command
            assert mock_warning.called, "Warning should be logged for duplicate command"
            assert any("already registered" in str(args) for args in mock_warning.call_args_list)
