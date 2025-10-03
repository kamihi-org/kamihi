"""
Functional tests for the CLI run command.

License:
    MIT

"""

from typing import Generator

import pytest
from pytest_docker_tools.wrappers import Container

from tests.conftest import KamihiContainer


@pytest.fixture
def kamihi(kamihi_container: KamihiContainer, request) -> Generator[Container, None, None]:
    """Fixture that ensures the Kamihi container is started and ready."""
    kamihi_container.uv_sync()
    kamihi_container.db_migrate()
    kamihi_container.db_upgrade()

    yield kamihi_container


def test_run(kamihi: KamihiContainer):
    """Test the run command."""
    kamihi.start("kamihi run --host=localhost --port=4242")


@pytest.mark.parametrize("level", ["TRACE", "DEBUG", "INFO", "SUCCESS"])
def test_run_log_level(kamihi: KamihiContainer, level: str):
    """Test the run command with all possible log levels."""
    kamihi.start(f"kamihi run --log-level={level}")


@pytest.mark.parametrize("level", ["INVALID", "debug", "20"])
def test_run_log_level_invalid(kamihi: KamihiContainer, level: str):
    """Test the run command with an invalid log level."""
    kamihi.run_command_and_wait_for_message(
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
    kamihi.run_command_and_wait_for_log(
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
    kamihi.run_command_and_wait_for_message(
        f"kamihi run --host={host}",
        "Invalid value for '--host'",
    )


@pytest.mark.parametrize("port", [2000, 65535])
def test_run_web_port(kamihi: KamihiContainer, port):
    """Test the run command with various valid web port options."""
    kamihi.run_command_and_wait_for_log(
        f"kamihi run --port={port}",
        "Web server started on",
        "INFO",
        {"host": "0.0.0.0", "port": port},
    )


@pytest.mark.parametrize("port", [-1, 0, 65536, "invalid", "80.80"])
def test_run_web_port_invalid(kamihi: KamihiContainer, port):
    """Test the run command with various invalid web port options."""
    kamihi.run_command_and_wait_for_message(
        f"kamihi run --port={port}",
        "Invalid value for '--port'",
    )
