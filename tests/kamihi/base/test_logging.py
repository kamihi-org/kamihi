"""
Tests for the kamihi.base.logging module.

License:
    MIT

"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from loguru import logger

from kamihi.base.config import LogSettings
from kamihi.base.logging import configure_logging


@pytest.fixture
def mock_logger():
    """
    Fixture to provide a mock logger instance.
    """
    return logger.bind()


def test_initialization_removes_existing_handlers(mock_logger):
    # Setup
    settings = LogSettings()

    with patch.object(mock_logger, "remove") as mock_remove:
        # Execute
        configure_logging(mock_logger, settings)

        # Verify
        mock_remove.assert_called_once()


@pytest.mark.parametrize(
    "handler_type, enable_param, handler_value, check_function",
    [
        ("stdout", "stdout_enable", sys.stdout, lambda call, val: call.args[0] == val),
        ("stderr", "stderr_enable", sys.stderr, lambda call, val: call.args[0] == val),
        ("file", "file_enable", "test.log", lambda call, val: call.args[0] == val),
        (
            "notification",
            "notification_enable",
            None,  # Special case handled in test
            None,  # Special case handled in test
        ),
    ],
)
def test_handler_configuration(mock_logger, handler_type, enable_param, handler_value, check_function):
    # Test when handler is enabled
    settings_kwargs = {enable_param: True}

    # Special handling for file and notification
    if handler_type == "file":
        settings_kwargs["file_path"] = handler_value
    elif handler_type == "notification":
        settings_kwargs["notification_urls"] = ["discord://webhook_id/webhook_token"]

    settings = LogSettings(**settings_kwargs)

    if handler_type == "notification":
        with (
            patch("kamihi.base.logging.ManualSender", autospec=True) as mock_sender_class,
            patch.object(mock_logger, "add") as mock_add,
        ):
            mock_sender = MagicMock()
            mock_sender_class.return_value = mock_sender

            # Execute
            configure_logging(mock_logger, settings)

            # Verify
            mock_sender_class.assert_called_once_with(settings.notification_urls)
            assert any(call.args[0] == mock_sender.notify for call in mock_add.call_args_list)
    else:
        with patch.object(mock_logger, "add") as mock_add:
            # Execute
            configure_logging(mock_logger, settings)

            # Verify
            assert any(check_function(call, handler_value) for call in mock_add.call_args_list)

    # Test when handler is disabled
    settings_kwargs = {enable_param: False}
    settings = LogSettings(**settings_kwargs)

    if handler_type == "notification":
        with (
            patch("kamihi.base.manual_send.ManualSender") as mock_sender_class,
            patch.object(mock_logger, "add") as mock_add,
        ):
            # Execute
            configure_logging(mock_logger, settings)

            # Verify
            mock_sender_class.assert_not_called()
    else:
        with patch.object(mock_logger, "add") as mock_add:
            # Execute
            configure_logging(mock_logger, settings)

            # Verify
            if handler_type == "file":
                assert not any(call.args[0] == handler_value for call in mock_add.call_args_list if len(call.args) > 0)
            else:
                assert not any(check_function(call, handler_value) for call in mock_add.call_args_list)


@pytest.mark.parametrize(
    "handler_type, level_param, level_value, handler_arg",
    [
        ("stdout", "stdout_level", "INFO", sys.stdout),
        ("stderr", "stderr_level", "ERROR", sys.stderr),
        ("file", "file_level", "DEBUG", "test.log"),
        ("notification", "notification_level", "CRITICAL", None),
    ],
)
def test_log_level_configuration(mock_logger, handler_type, level_param, level_value, handler_arg):
    # Setup
    settings_kwargs = {
        "stdout_enable": False,
        "stderr_enable": False,
        "file_enable": False,
        "notification_enable": False,
        level_param: level_value,
    }

    # Enable specific handler being tested
    enable_param = f"{handler_type}_enable"
    settings_kwargs[enable_param] = True

    if handler_type == "file":
        settings_kwargs["file_path"] = handler_arg
    elif handler_type == "notification":
        settings_kwargs["notification_urls"] = ["discord://webhook_id/webhook_token"]

    settings = LogSettings(**settings_kwargs)

    if handler_type == "notification":
        with (
            patch("kamihi.base.logging.ManualSender", autospec=True) as mock_sender_class,
            patch.object(mock_logger, "add") as mock_add,
        ):
            mock_sender = MagicMock()
            mock_sender_class.return_value = mock_sender

            # Execute
            configure_logging(mock_logger, settings)

            # Verify notification level
            notification_call = next(call for call in mock_add.call_args_list if call.args[0] == mock_sender.notify)
            assert notification_call.kwargs["level"] == level_value
    else:
        with patch.object(mock_logger, "add") as mock_add:
            # Execute
            configure_logging(mock_logger, settings)

            # Verify level
            handler_call = next(call for call in mock_add.call_args_list if call.args and call.args[0] == handler_arg)
            assert handler_call.kwargs["level"] == level_value


@pytest.mark.parametrize(
    "handler_type, serialize_param, serialize_value, handler_arg",
    [
        ("stdout", "stdout_serialize", True, sys.stdout),
        ("stderr", "stderr_serialize", False, sys.stderr),
        ("file", "file_serialize", True, "test.log"),
    ],
)
def test_serialize_configuration(mock_logger, handler_type, serialize_param, serialize_value, handler_arg):
    # Setup
    settings_kwargs = {
        "stdout_enable": False,
        "stderr_enable": False,
        "file_enable": False,
        serialize_param: serialize_value,
    }

    # Enable specific handler being tested
    enable_param = f"{handler_type}_enable"
    settings_kwargs[enable_param] = True

    if handler_type == "file":
        settings_kwargs["file_path"] = handler_arg

    settings = LogSettings(**settings_kwargs)

    with patch.object(mock_logger, "add") as mock_add:
        # Execute
        configure_logging(mock_logger, settings)

        # Verify serialization setting
        handler_call = next(call for call in mock_add.call_args_list if call.args and call.args[0] == handler_arg)
        assert handler_call.kwargs["serialize"] is serialize_value
