"""
Docker container creation and management fixtures.

License:
    MIT

"""

import json
import sqlite3
import tempfile
from typing import Any, Generator

import docker.models
import pytest
from docker.types import CancellableStream
from pytest_docker_tools import build, volume, fxtr, container
from pytest_docker_tools.wrappers import Container


@pytest.fixture
def db_url() -> str:
    """Fixture to provide the database URL."""
    return "sqlite:///./kamihi.db"


class EndOfLogsException(Exception):
    """Exception raised when the end of logs is reached without finding the expected log entry."""


class KamihiContainer(Container):
    """
    Custom container class for Kamihi.

    This class is used to provide a custom container for the Kamihi application.
    It allows for additional functionality or customization if needed in the future.
    """

    command_logs: list[str]

    _container: docker.models.containers.Container

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_logs = []

    @staticmethod
    def parse_log_json(line: str) -> dict | None:
        """
        Parse a log line from the Kamihi container.

        Args:
            line (str): The log line to parse.

        Returns:
            dict: The parsed log entry as a dictionary.
        """
        res = json.loads(line)
        assert isinstance(res, dict), "Log entry is not a dictionary"
        assert "record" in res, "Log entry does not contain 'record' key"
        assert "level" in res["record"], "Log entry does not contain 'level' key"
        assert "name" in res["record"]["level"], "Log entry does not contain 'name' key in 'level'"
        assert "message" in res["record"], "Log entry does not contain 'message' key"
        return res

    def wait_for_log(
        self,
        stream: CancellableStream,
        message: str,
        level: str = "INFO",
        extra_values: dict[str, Any] = None,
        parse_json: bool = True,
    ) -> dict | str | None:
        """
        Wait for a specific log entry in the Kamihi container.

        Args:
            message (str): The message to wait for in the log entry.
            level (str): The log level to wait for (e.g., "INFO", "ERROR").
            extra_values (dict[str, Any], optional): Additional key-value pairs to match in the log entry's extra dictionary.
            stream (Generator, optional): A generator that yields log lines from the container.
            parse_json (bool): Whether to parse the log entry as JSON.

        Returns:
            dict | str: The log entry or message that matches the specified level and message, or None if not found.
        """
        self.command_logs.append(f"Waiting for log: level={level}, message={message}, extra_values={extra_values}")

        for raw_line in stream:
            for line in raw_line.decode().splitlines():
                line = line.strip()
                self.command_logs.append(line)

                if not parse_json and message in line:
                    return line

                try:
                    log_entry = self.parse_log_json(line)
                except (json.JSONDecodeError, AssertionError):
                    continue

                record = log_entry.get("record", {})
                level_name = record.get("level", {}).get("name")
                msg = record.get("message", "")

                if level_name == level and message in msg:
                    if extra_values:
                        extras = record.get("extra", {})
                        if not all(item in extras.items() for item in extra_values.items()):
                            continue

                    return log_entry

        raise EndOfLogsException(
            "End of logs reached without finding the expected log entry: "
            f"message={message}, level={level}, extra_values={extra_values}"
        )

    def wait_for_message(self, message: str, stream: CancellableStream = None) -> str:
        """
        Wait for a specific message in the Kamihi container logs, without parsing it as JSON.

        Args:
            message (str): The message to wait for.
            stream (Generator, optional): A generator that yields log lines from the container.

        Returns:
            dict: The log entry that matches the specified message.
        """
        return self.wait_for_log(stream, message, parse_json=False)

    def run_command(self, command: str) -> CancellableStream:
        """Run a command in the Kamihi container and return the output stream."""
        self.command_logs.append(f"$ {command}")
        return self._container.exec_run(command, stream=True).output

    def run_command_and_wait_for_log(
        self,
        command: str,
        message: str,
        level: str = "INFO",
        extra_values: dict[str, Any] = None,
        parse_json: bool = True,
    ) -> dict | None:
        """
        Run a command in the Kamihi container and wait for a specific log entry.

        Args:
            command (str): The command to run in the container.
            message (str): The message to wait for in the log entry.
            level (str): The log level to wait for (e.g., "INFO", "ERROR").
            extra_values (dict[str, Any], optional): Additional key-value pairs to match in the log entry's extra dictionary.
            parse_json (bool): Whether to parse the log entry as JSON.

        Returns:
            dict: The log entry that matches the specified level and message.
        """
        stream = self.run_command(command)
        return self.wait_for_log(stream, message, level, extra_values, parse_json=parse_json)

    def run_command_and_wait_for_message(self, command: str, message: str) -> dict | None:
        """
        Run a command in the Kamihi container and wait for a specific log message.

        Args:
            command (str): The command to run in the container.
            message (str): The message to wait for in the log entry.

        Returns:
            dict: The log entry that matches the specified message.
        """
        return self.run_command_and_wait_for_log(command, message, parse_json=False)

    def uv_sync(self, command: str = "uv sync") -> None:
        """
        Sync the Kamihi application in the container.

        Args:
            command (str): The command to sync the application. Defaults to "uv sync".
        """
        stream = self.run_command(command)
        for line in stream:
            line = line.decode().strip()
            self.command_logs.append(line)

    def db_migrate(self, command: str = "kamihi db migrate") -> None:
        """
        Run database migrations in the Kamihi container.

        Args:
            command (str): The command to run migrations. Defaults to "kamihi db migrate".
        """
        self.run_command_and_wait_for_log(command, "Migrated", "SUCCESS")

    def db_upgrade(self, command: str = "kamihi db upgrade") -> None:
        """
        Upgrade the database schema in the Kamihi container.

        Args:
            command (str): The command to upgrade the database. Defaults to "kamihi db upgrade".
        """
        self.run_command_and_wait_for_log(command, "Upgraded", "SUCCESS")

    def start(self, command: str = "kamihi run") -> None:
        """
        Run Kamihi in the container with the specified command.

        Args:
            command (str): The command to run Kamihi. Defaults to "kamihi run".
        """
        self.run_command_and_wait_for_log(command, "Started!", "SUCCESS")

    def stop(self) -> None:
        """
        Stop the Kamihi container gracefully.

        This method overrides the default stop method to ensure that the Kamihi container
        is stopped gracefully and waits for the logs to confirm the stop.
        """
        self.kill(signal="SIGKILL")

    def query_db(self, query: str) -> list[tuple]:
        """
        Execute a SQL query in the Kamihi container's SQLite database.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list[tuple]: The results of the query as a list of tuples.
        """
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(self.get_files("/app/kamihi.db")["kamihi.db"])

            conn = sqlite3.connect(tmp.name)
            cursor = conn.cursor()
            res = cursor.execute(query)
            res = cursor.fetchall()

            conn.close()

        return res


kamihi_image = build(path=".", dockerfile="tests/Dockerfile")
kamihi_volume = volume(initial_content=fxtr("app_folder"))
uv_cache_volume = volume(scope="session")
kamihi_container = container(
    image="{kamihi_image.id}",
    environment={
        "KAMIHI_TESTING": "True",
        "KAMIHI_TOKEN": "{test_settings.bot_token}",
        "KAMIHI_LOG__STDOUT_LEVEL": "TRACE",
        "KAMIHI_LOG__STDOUT_SERIALIZE": "True",
        "KAMIHI_WEB__HOST": "0.0.0.0",
        "KAMIHI_DB__URL": "{db_url}",
    },
    volumes={
        "{kamihi_volume.name}": {"bind": "/app"},
        "{uv_cache_volume.name}": {"bind": "/root/.cache/uv"},
    },
    command="sleep infinity",
    wrapper_class=KamihiContainer,
)


@pytest.fixture
def kamihi(kamihi_container: KamihiContainer, request) -> Generator[Container, None, None]:
    """Fixture that ensures the Kamihi container is started and ready."""
    kamihi_container.uv_sync()
    kamihi_container.db_migrate()
    kamihi_container.db_upgrade()
    kamihi_container.start()

    yield kamihi_container

    kamihi_container.stop()


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """
    Fixture to clean up the host environment after tests.

    This fixture is used to remove, containers, volumes, and images created during the tests.
    """
    yield

    request.config._docker_cleanup_report = {
        "containers": docker.from_env().containers.prune(),
        "volumes": docker.from_env().volumes.prune({"label": "creator=pytest-docker-tools"}),
        "images": docker.from_env().images.prune({"dangling": True}),
    }
