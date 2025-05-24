"""
Functional tests for the CLI run command.

License:
    MIT

"""

import pytest
from urllib3.exceptions import ReadTimeoutError


@pytest.mark.parametrize("run_command", ["kamihi run"])
def test_run(kamihi, wait_for_log, run_command):
    """Test the run command."""
    wait_for_log("SUCCESS", "Started!")


@pytest.mark.parametrize("run_command", ["kamihi run --log-level=SUCCESS"])
def test_run_log_level(kamihi, wait_for_log, run_command):
    """Test the run command with log level set to SUCCESS."""
    with pytest.raises(ReadTimeoutError):
        wait_for_log("TRACE", "Application startup complete.")


@pytest.mark.parametrize("run_command", ["kamihi run --log-level=INVALID"])
def test_run_invalid_log_level(kamihi_container, run_command, message_after_stopped):
    """Test the run command with an invalid log level."""
    message_after_stopped("Invalid value for '--log-level' / '-l': 'INVALID' is not one of")
