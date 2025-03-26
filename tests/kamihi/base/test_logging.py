"""
Tests for the kamihi.base.logging module.

License:
    MIT

"""

import sys
from unittest.mock import MagicMock, patch

from loguru import logger

from kamihi.base.config import LogSettings
from kamihi.base.logging import configure_logging


def test_initialization_removes_existing_handlers():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings()

    with patch.object(test_logger, "remove") as mock_remove:
        # Execute
        configure_logging(test_logger, settings)

        # Verify
        mock_remove.assert_called_once()


def test_stdout_handler_added_when_enabled():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(stdout_enable=True)

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify
        assert any(call.args[0] == sys.stdout for call in mock_add.call_args_list)


def test_stdout_handler_not_added_when_disabled():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(stdout_enable=False)

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify
        assert not any(call.args[0] == sys.stdout for call in mock_add.call_args_list)


def test_stderr_handler_added_when_enabled():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(stderr_enable=True)

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify
        assert any(call.args[0] == sys.stderr for call in mock_add.call_args_list)


def test_stderr_handler_not_added_when_disabled():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(stderr_enable=False)

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify
        assert not any(call.args[0] == sys.stderr for call in mock_add.call_args_list)


def test_file_handler_added_when_enabled():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(file_enable=True, file_path="test.log")

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify
        assert any(call.args[0] == settings.file_path for call in mock_add.call_args_list)


def test_file_handler_not_added_when_disabled():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(file_enable=False)

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify
        assert not any(call.args[0] == settings.file_path for call in mock_add.call_args_list if len(call.args) > 0)


def test_notification_handler_added_when_enabled():
    # Setup
    test_logger = logger.bind()
    urls = ["discord://webhook_id/webhook_token"]
    settings = LogSettings(notification_enable=True, notification_urls=urls)

    with (
        patch("kamihi.base.logging.ManualSender", autospec=True) as mock_sender_class,
        patch.object(test_logger, "add") as mock_add,
    ):
        mock_sender = MagicMock()
        mock_sender_class.return_value = mock_sender

        # Execute
        configure_logging(test_logger, settings)

        # Verify
        mock_sender_class.assert_called_once_with(urls)
        assert any(call.args[0] == mock_sender.notify for call in mock_add.call_args_list)


def test_notification_handler_not_added_when_disabled():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(notification_enable=False)

    with (
        patch("kamihi.base.manual_send.ManualSender") as mock_sender_class,
        patch.object(test_logger, "add") as mock_add,
    ):
        mock_sender = MagicMock()
        mock_sender_class.return_value = mock_sender

        # Execute
        configure_logging(test_logger, settings)

        # Verify
        mock_sender_class.assert_not_called()


def test_configuration_applies_correct_log_levels():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(
        stdout_enable=True,
        stdout_level="INFO",
        stderr_enable=True,
        stderr_level="ERROR",
        file_enable=True,
        file_level="DEBUG",
        file_path="test.log",
        notification_enable=True,
        notification_level="CRITICAL",
    )

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify levels for each handler
        calls = mock_add.call_args_list
        stdout_call = next(call for call in calls if call.args and call.args[0] == sys.stdout)
        stderr_call = next(call for call in calls if call.args and call.args[0] == sys.stderr)
        file_call = next(call for call in calls if call.args and call.args[0] == settings.file_path)

        assert stdout_call.kwargs["level"] == "INFO"
        assert stderr_call.kwargs["level"] == "ERROR"
        assert file_call.kwargs["level"] == "DEBUG"

        # The notification call is harder to identify directly, but we can check it exists
        assert any("level" in call.kwargs and call.kwargs["level"] == "CRITICAL" for call in calls)


def test_configuration_applies_serialize_settings():
    # Setup
    test_logger = logger.bind()
    settings = LogSettings(
        stdout_enable=True,
        stdout_serialize=True,
        stderr_enable=True,
        stderr_serialize=False,
        file_enable=True,
        file_serialize=True,
        file_path="test.log",
    )

    with patch.object(test_logger, "add") as mock_add:
        # Execute
        configure_logging(test_logger, settings)

        # Verify serialize settings
        calls = mock_add.call_args_list
        stdout_call = next(call for call in calls if call.args and call.args[0] == sys.stdout)
        stderr_call = next(call for call in calls if call.args and call.args[0] == sys.stderr)
        file_call = next(call for call in calls if call.args and call.args[0] == settings.file_path)

        assert stdout_call.kwargs["serialize"] is True
        assert stderr_call.kwargs["serialize"] is False
        assert file_call.kwargs["serialize"] is True
