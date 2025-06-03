"""
Functional tests for the CLI run command.

License:
    MIT

"""

import pytest

from tests.functional.conftest import KamihiContainer


@pytest.fixture
def run_command():
    """
    Override the run command to a simple sleep command so
    we can test the run functionality without needing
    the full application to start.
    """
    return "sleep infinity"


def test_run(kamihi: KamihiContainer):
    """Test the run command."""
    kamihi.run_and_wait_for_log(
        "kamihi run --host=localhost --port=4242",
        "Started!",
        "SUCCESS",
    )


@pytest.mark.parametrize("level", ["TRACE", "DEBUG", "INFO", "SUCCESS"])
def test_run_log_level(kamihi: KamihiContainer, level: str):
    """Test the run command with all possible log levels."""
    kamihi.run_and_wait_for_log(
        f"kamihi run --log-level={level}",
        "Started!",
        "SUCCESS",
    )


@pytest.mark.parametrize("level", ["INVALID", "debug", "20"])
def test_run_log_level_invalid(kamihi: KamihiContainer, level: str):
    """Test the run command with an invalid log level."""
    kamihi.run_and_wait_for_message(
        f"kamihi run --log-level={level}",
        "Invalid value for '--log-level'",
    )


@pytest.mark.parametrize(
    "host",
    [
        "localhost",
    ],
)
def test_run_web_host(kamihi: KamihiContainer, host):
    """Test the run command with various valid web host options."""
    kamihi.run_and_wait_for_log(
        f"kamihi run --host={host}", "Web server started on", "INFO", {"host": host, "port": 4242}
    )


@pytest.mark.parametrize(
    "host",
    [
        "localhost:4242",
        "with-slash.com/",
    ],
)
def test_run_web_host_invalid(kamihi: KamihiContainer, host):
    """Test the run command with various invalid web host options."""
    kamihi.run_and_wait_for_message(
        f"kamihi run --host={host}",
        "Invalid value for '--host'",
    )


@pytest.mark.parametrize("port", [2000, 65535])
def test_run_web_port(kamihi: KamihiContainer, port):
    """Test the run command with various valid web port options."""
    kamihi.run_and_wait_for_log(
        f"kamihi run --port={port}",
        "Web server started on",
        "INFO",
        {"host": "0.0.0.0", "port": port},
    )


@pytest.mark.parametrize("port", [-1, 0, 65536, "invalid", "80.80"])
def test_run_web_port_invalid(kamihi: KamihiContainer, port):
    """Test the run command with various invalid web port options."""
    kamihi.run_and_wait_for_message(
        f"kamihi run --port={port}",
        "Invalid value for '--port'",
    )
