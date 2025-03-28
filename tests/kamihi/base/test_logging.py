"""
Tests for the kamihi.base.logging module.

License:
    MIT

"""

import os
import sys
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest
from loguru import logger

from kamihi.base.config import LogSettings
from kamihi.base.logging import configure_logging


@pytest.fixture
def mock_logger():
    """Fixture to provide a mock logger instance."""
    return logger.bind()


def test_log_message_recorded(mock_logger):
    """
    Test that log messages are correctly recorded with the appropriate severity level.

    This test verifies the requirement that when a developer adds a log message,
    the system correctly records it with the appropriate severity level.
    """
    # Create a temporary file for logging
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Setup with file logging enabled
        settings = LogSettings(
            stdout_enable=False, stderr_enable=False, file_enable=True, file_path=temp_path, file_level="DEBUG"
        )

        # Configure logging
        configure_logging(mock_logger, settings)

        # Log messages at different severity levels
        test_messages = {
            "debug": "Debug test message",
            "info": "Info test message",
            "warning": "Warning test message",
            "error": "Error test message",
            "critical": "Critical test message",
        }

        for level_name, message in test_messages.items():
            level_method = getattr(mock_logger, level_name)
            level_method(message)

        # Give a moment for file writing to complete
        time.sleep(0.1)

        # Read the log file
        with open(temp_path, "r") as f:
            log_content = f.read()

        # Verify each message was recorded with correct severity
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level, message in zip(expected_levels, test_messages.values()):
            assert level in log_content and message in log_content

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_log_levels(mock_logger):
    """
    Test that log messages are filtered according to the configured severity level.

    This test verifies that when configuring a specific log level, only messages
    at that level or higher are recorded, while lower-level messages are filtered out.
    """
    # Create a temporary file for logging
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Setup with file logging enabled and INFO level
        settings = LogSettings(
            stdout_enable=False,
            stderr_enable=False,
            file_enable=True,
            file_path=temp_path,
            file_level="INFO",  # Only INFO and above should be recorded
        )

        # Configure logging
        configure_logging(mock_logger, settings)

        # Log messages at different severity levels
        mock_logger.debug("Debug test message")
        mock_logger.info("Info test message")
        mock_logger.warning("Warning test message")
        mock_logger.error("Error test message")
        mock_logger.critical("Critical test message")

        # Give a moment for file writing to complete
        time.sleep(0.1)

        # Read the log file
        with open(temp_path, "r") as f:
            log_content = f.read()

        # Verify messages were filtered correctly
        assert "Debug test message" not in log_content  # Should be filtered out
        assert "Info test message" in log_content
        assert "Warning test message" in log_content
        assert "Error test message" in log_content
        assert "Critical test message" in log_content

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_log_message_serialized(mock_logger):
    """
    Test that log messages are serialized in JSON format when serialization is enabled.

    This test verifies that when serialization is enabled, the system stores logs
    in a standardized format (JSON) that allows for subsequent analysis and processing.
    """
    # Create a temporary file for logging
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Setup with file logging enabled and serialization enabled
        settings = LogSettings(
            stdout_enable=False,
            stderr_enable=False,
            file_enable=True,
            file_path=temp_path,
            file_level="INFO",
            file_serialize=True,  # Enable serialization
        )

        # Configure logging
        configure_logging(mock_logger, settings)

        # Log a test message
        test_message = "This is a test message for serialization"
        mock_logger.info(test_message)

        # Give a moment for file writing to complete
        time.sleep(0.1)

        # Read the log file
        with open(temp_path, "r") as f:
            log_content = f.read().strip()

        # Verify the content is valid JSON
        import json

        log_record = json.loads(log_content)

        # Verify the JSON contains our message
        assert test_message in log_record["text"]

        # Verify other expected fields in the JSON structure
        assert "time" in log_record["record"].keys()
        assert "level" in log_record["record"].keys()
        assert "name" in log_record["record"].keys()

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_log_rotation(mock_logger):
    """
    Test that log files are automatically rotated when they reach size/age limits.

    This test verifies that when logs reach their configured maximum size or age,
    the system automatically rotates them to prevent filesystem saturation and
    information loss.
    """
    # Create a temporary directory for log files
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = os.path.join(temp_dir, "test_rotation.log")

        # Configure logging with small size rotation threshold (1 KB)
        settings = LogSettings(
            stdout_enable=False,
            stderr_enable=False,
            file_enable=True,
            file_path=log_path,
            file_level="INFO",
            file_rotation="1 KB",  # Rotate after 1 KB
        )

        configure_logging(mock_logger, settings)

        # Write enough logs to trigger rotation (more than 1 KB)
        long_message = "X" * 100  # 100 characters
        for i in range(20):  # Should write >1KB total
            mock_logger.info(f"{i}: {long_message}")

        # Give time for file operations to complete
        time.sleep(0.2)

        # Check for rotated log files (should be main log file + at least one rotated file)
        log_files = [f for f in os.listdir(temp_dir) if f.startswith("test_rotation")]

        # Should have at least 2 files (the current log and at least one rotated log)
        assert len(log_files) >= 2, f"Expected at least 2 log files, found {len(log_files)}"

        # Verify main log file exists
        assert os.path.exists(log_path)


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
            matching_calls = [call for call in mock_add.call_args_list if call.args[0] == mock_sender.notify]
            assert matching_calls, "No call to mock_add with mock_sender.notify was found"
            notification_call = matching_calls[0]
            assert notification_call.kwargs["level"] == level_value
    else:
        with patch.object(mock_logger, "add") as mock_add:
            # Execute
            configure_logging(mock_logger, settings)

            # Verify level
            matching_calls = [call for call in mock_add.call_args_list if call.args and call.args[0] == handler_arg]
            assert matching_calls, f"No call with handler_arg {handler_arg} found in mock_add.call_args_list"
            handler_call = matching_calls[0]
            assert (
                handler_call.kwargs["level"] == level_value
            ), f"Expected level {level_value}, got {handler_call.kwargs['level']}"


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
        matching_calls = [call for call in mock_add.call_args_list if call.args and call.args[0] == handler_arg]
        assert matching_calls, f"No call with handler_arg {handler_arg} found in mock_add.call_args_list"
        handler_call = matching_calls[0]
        assert (
            handler_call.kwargs["serialize"] == serialize_value
        ), f"Expected serialize value {serialize_value}, got {handler_call.kwargs['level']}"
