"""
Common fixtures for functional tests.

License:
    MIT

"""

import json
from pathlib import Path
from textwrap import dedent
from typing import Any, AsyncGenerator, Generator

import docker.models.containers
import pytest
from docker.types import CancellableStream
from dotenv import load_dotenv
from playwright.async_api import Page
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient
from pytest_docker_tools.wrappers import Container
from pytest_docker_tools import build, container, fetch, volume, fxtr
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation


class TestingSettings(BaseSettings):
    """
    Settings for the testing environment.

    Attributes:
        bot_token (str): The bot token for the Telegram bot.
        bot_username (str): The username of the bot.
        user_id (int): The user ID for testing.
        tg_phone_number (str): The phone number for Telegram authentication.
        tg_api_id (int): The API ID for Telegram authentication.
        tg_api_hash (str): The API hash for Telegram authentication.
        tg_session (str): The session string for Telegram authentication.
        tg_dc_id (int): The data center ID for Telegram authentication.
        tg_dc_ip (str): The data center IP address for Telegram authentication.
        wait_time (int): The wait time between requests.

    """

    bot_token: str = Field()
    bot_username: str = Field()
    user_id: int = Field()
    tg_phone_number: str = Field()
    tg_api_id: int = Field()
    tg_api_hash: str = Field()
    tg_session: str = Field()
    tg_dc_id: int = Field()
    tg_dc_ip: str = Field()
    wait_time: float = Field(default=0.5)

    model_config = SettingsConfigDict(
        env_prefix="KAMIHI_TESTING__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
        yaml_file="kamihi.yaml",
    )


@pytest.fixture(scope="session")
def test_settings() -> TestingSettings:
    """
    Fixture to provide the testing settings.

    Returns:
        TestingSettings: The testing settings.

    """
    return TestingSettings()


@pytest.fixture(scope="session")
async def tg_client(test_settings):
    """Fixture to create a test Telegram client for the application."""
    load_dotenv()

    client = TelegramClient(
        StringSession(test_settings.tg_session),
        test_settings.tg_api_id,
        test_settings.tg_api_hash,
        sequential_updates=True,
    )
    client.session.set_dc(
        test_settings.tg_dc_id,
        test_settings.tg_dc_ip,
        443,
    )
    await client.connect()
    await client.sign_in(phone=test_settings.tg_phone_number)

    yield client

    await client.disconnect()
    await client.disconnected


@pytest.fixture(scope="session")
async def chat(test_settings, tg_client) -> AsyncGenerator[Conversation, Any]:
    """Open conversation with the bot."""
    async with tg_client.conversation(test_settings.bot_username, timeout=60, max_messages=10000) as conv:
        yield conv


@pytest.fixture
def pyproject() -> dict:
    """Fixture to provide the path to the pyproject.toml file."""
    return {
        "pyproject.toml": """\
            [project]
            name = "kftp"
            version = "0.0.0"
            description = "kftp"
            requires-python = ">=3.12"
            dependencies = [
                "kamihi",
            ]
            
            [tool.uv.sources]
            kamihi = { path = "/lib/kamihi" }
        """
    }


@pytest.fixture
def config_file() -> dict:
    """Fixture to provide the path to the kamihi.yaml file."""
    return {"kamihi.yaml": ""}


@pytest.fixture
def actions_folder() -> dict:
    """Fixture to provide the path to the actions folder."""
    return {}


@pytest.fixture
def models_folder() -> dict:
    """Fixture to provide the path to the models folder."""
    return {}


@pytest.fixture
def app_folder(pyproject, config_file, actions_folder, models_folder) -> dict:
    """Fixture to provide the path to the app folder."""
    res = {}
    res.update({key: dedent(value) for key, value in pyproject.items()})
    res.update({key: dedent(value) for key, value in config_file.items()})
    res.update(
        {"actions/" + key: dedent(value) if isinstance(value, str) else value for key, value in actions_folder.items()}
    )
    res.update(
        {"models/" + key: dedent(value) if isinstance(value, str) else value for key, value in models_folder.items()}
    )
    res = {key: value.encode() if isinstance(value, str) else value for key, value in res.items()}
    return res


@pytest.fixture
def run_command():
    """Fixture to provide the command for the bot."""
    return "kamihi run"


@pytest.fixture
def sync_and_run_command(run_command):
    """Fixture to provide the command for the bot."""
    return f"uv run {run_command}"


class EndOfLogsException(Exception):
    """Exception raised when the end of logs is reached without finding the expected log entry."""


class KamihiContainer(Container):
    """
    Custom container class for Kamihi.

    This class is used to provide a custom container for the Kamihi application.
    It allows for additional functionality or customization if needed in the future.
    """

    _container: docker.models.containers.Container

    def logs(self, stream: bool = False) -> CancellableStream | list[str]:
        """
        Get the logs of the Kamihi container.

        Args:
            stream (bool): If True, stream the logs. If False, return the logs as a list.
        """
        if stream:
            return self._container.logs(stream=True)
        return self._container.logs().decode().split("\n")

    @staticmethod
    def parse_log_json(line: str) -> dict | None:
        """
        Parse a log line from the Kamihi container.

        Args:
            line (str): The log line to parse.

        Returns:
            dict: The parsed log entry as a dictionary.
        """
        try:
            res = json.loads(line.strip())
            assert isinstance(res, dict), "Log entry is not a dictionary"
            assert "record" in res, "Log entry does not contain 'record' key"
            assert "level" in res["record"], "Log entry does not contain 'level' key"
            assert "name" in res["record"]["level"], "Log entry does not contain 'name' key in 'level'"
            assert "message" in res["record"], "Log entry does not contain 'message' key"
            return res
        except (json.JSONDecodeError, AssertionError):
            return None

    def wait_for_log(
        self,
        message: str,
        level: str = "INFO",
        extra_values: dict[str, Any] = None,
        stream: CancellableStream = None,
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
        if stream is None:
            stream = self.logs(stream=True)
        for line in stream:
            line = line.decode().strip()
            if parse_json:
                log_entry = self.parse_log_json(line)
                if (
                    log_entry
                    and log_entry["record"]["level"]["name"] == level
                    and message in log_entry["record"]["message"]
                ):
                    if extra_values:
                        if all(item in log_entry["record"].get("extra", {}).items() for item in extra_values.items()):
                            return log_entry
                    else:
                        return log_entry
            else:
                log_entry = line
                if message in log_entry:
                    return log_entry
        return None

    def wait_for_message(self, message: str, stream: CancellableStream = None) -> str:
        """
        Wait for a specific message in the Kamihi container logs, without parsing it as JSON.

        Args:
            message (str): The message to wait for.
            stream (Generator, optional): A generator that yields log lines from the container.

        Returns:
            dict: The log entry that matches the specified message.
        """
        return self.wait_for_log(message, stream=stream, parse_json=False)

    def assert_logged(self, level: str, message: str) -> dict | None:
        """Assert that the log entry was found."""
        for line in self.logs():
            log_entry = self.parse_log_json(line)
            if (
                log_entry
                and log_entry["record"]["level"]["name"] == level
                and message in log_entry["record"]["message"]
            ):
                return log_entry
        raise EndOfLogsException()

    def wait_until_started(self) -> None:
        """
        Wait until the Kamihi container is started.

        This method overrides the default wait_until_started method to ensure that
        the Kamihi container is ready before proceeding with tests.
        """
        self.wait_for_log("Started!", "SUCCESS")

    def run(self, command: str) -> CancellableStream:
        """Run a command in the Kamihi container and return the output stream."""
        return self._container.exec_run(command, stream=True).output

    def run_and_wait_for_log(
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
        stream = self.run(command)
        return self.wait_for_log(message, level, extra_values, stream=stream, parse_json=parse_json)

    def run_and_wait_for_message(self, command: str, message: str) -> dict | None:
        """
        Run a command in the Kamihi container and wait for a specific log message.

        Args:
            command (str): The command to run in the container.
            message (str): The message to wait for in the log entry.

        Returns:
            dict: The log entry that matches the specified message.
        """
        return self.run_and_wait_for_log(command, message, parse_json=False)

    def stop(self) -> None:
        """
        Stop the Kamihi container gracefully.

        This method overrides the default stop method to ensure that the Kamihi container
        is stopped gracefully and waits for the logs to confirm the stop.
        """
        self.kill(signal="SIGINT")
        self.kill(signal="SIGINT")
        self.wait_for_log("Stopped!", "SUCCESS")


mongo_image = fetch(repository="mongo:latest")
"""Fixture that fetches the mongodb container image."""


mongo_volume = volume()
"""Fixture that creates a volume for the mongodb container."""


mongo_container = container(image="{mongo_image.id}", volumes={"{mongo_volume.name}": {"bind": "/data/db"}})
"""Fixture that provides the mongodb container."""


kamihi_image = build(path=".", dockerfile="tests/functional/Dockerfile")
"""Fixture that builds the kamihi container image."""


kamihi_volume = volume(initial_content=fxtr("app_folder"))
"""Fixture that creates a volume for the kamihi container."""


kamihi_container = container(
    image="{kamihi_image.id}",
    environment={
        "KAMIHI_TESTING": "True",
        "KAMIHI_TOKEN": "{test_settings.bot_token}",
        "KAMIHI_LOG__STDOUT_LEVEL": "TRACE",
        "KAMIHI_LOG__STDOUT_SERIALIZE": "True",
        "KAMIHI_DB__HOST": "mongodb://{mongo_container.ips.primary}",
        "KAMIHI_WEB__HOST": "0.0.0.0",
    },
    volumes={
        "{kamihi_volume.name}": {"bind": "/app"},
        str(Path("~/.cache/uv").expanduser()): {"bind": "/root/.cache/uv"},
    },
    command="{sync_and_run_command}",
    wrapper_class=KamihiContainer,
)
"""Fixture that provides the Kamihi container."""


@pytest.fixture
def kamihi(kamihi_container: KamihiContainer, run_command, request) -> Generator[Container, None, None]:
    """Fixture that ensures the Kamihi container is started and ready."""
    kamihi_container.wait_for_message("Bytecode compiled")
    if "kamihi run" in run_command:
        kamihi_container.wait_until_started()

    yield kamihi_container

    if request.node.rep_call.failed:
        title = f" Kamihi container logs for {request.node.name} "
        print(f"\n{title:=^80}")
        for line in kamihi_container.logs():
            if jline := kamihi_container.parse_log_json(line):
                print(jline["text"].strip())
            else:
                print(line.strip())
    if run_command == "kamihi run":
        kamihi_container.stop()


@pytest.fixture
async def admin_page(kamihi: KamihiContainer, page) -> Page:
    """Fixture that provides the admin page of the Kamihi web interface."""
    kamihi.assert_logged("TRACE", "Uvicorn running on http://0.0.0.0:4242 (Press CTRL+C to quit)")
    await page.goto(f"http://{kamihi.ips.primary}:4242/")
    return page


@pytest.fixture
def mongodb(mongo_container: Container) -> Generator[MongoClient, None, None]:
    """Fixture that provides the MongoDB container."""
    client = MongoClient(f"mongodb://{mongo_container.ips.primary}:27017")

    yield client.kamihi

    client.close()


@pytest.fixture
def user_custom_data():
    """Fixture to provide the user custom data."""
    return {}


@pytest.fixture
async def user_in_db(kamihi: KamihiContainer, test_settings, user_custom_data, mongodb):
    """Fixture that creates a user in the MongoDB database."""
    kamihi.run_and_wait_for_log(
        f"kamihi user add {test_settings.user_id} --data '{json.dumps(user_custom_data)}'",
        level="SUCCESS",
        message="User added.",
    )

    yield mongodb.user.find_one({"telegram_id": test_settings.user_id})


@pytest.fixture
async def add_permission_for_user(test_settings, mongodb):
    """Fixture that returns a function to add permissions to a user for an action in the MongoDB database."""

    def _add_permission(user: dict, action_name: str):
        action_id = mongodb.registered_action.find_one({"name": action_name})["_id"]
        user_id = mongodb.user.find_one({"telegram_id": user["telegram_id"]})["_id"]
        mongodb.permission.insert_one({"action": action_id, "users": [user_id], "roles": []})

    yield _add_permission


@pytest.fixture(scope="session")
def cleanup():
    """
    Fixture to clean up the host environment after tests.

    This fixture is used to remove, containers, volumes, and images created during the tests.
    """
    yield

    print(docker.from_env().containers.prune())
    print(docker.from_env().volumes.prune())
    print(docker.from_env().images.prune({"dangling": True}))
