"""
Common fixtures for functional tests.

License:
    MIT

"""

import json
import time
from pathlib import Path
from textwrap import dedent
from typing import Any, AsyncGenerator, Generator

import pytest
from dotenv import load_dotenv
from mongoengine import connect, disconnect
from playwright.async_api import Page
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytest_docker_tools.wrappers import Container
from pytest_docker_tools import build, container, fetch, volume, fxtr
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation

from kamihi.bot.models import RegisteredAction
from kamihi.users import User, Permission


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
    async with tg_client.conversation(test_settings.bot_username, timeout=10, max_messages=10000) as conv:
        yield conv


@pytest.fixture
def user_code():
    """Fixture to provide the user code for the bot."""
    return {
        "main.py": dedent("""\
                         from kamihi import bot
                         bot.start()
                         """).encode()
    }


mongo_image = fetch(repository="mongo:latest")
"""Fixture that fetches the mongodb container image."""


mongo_container = container(image="{mongo_image.id}")
"""Fixture that provides the mongodb container."""


kamihi_image = build(path=".", dockerfile="tests/functional/docker/Dockerfile")
"""Fixture that builds the kamihi container image."""


kamihi_volume = volume(initial_content=fxtr("user_code"))
"""Fixture that creates a volume for the kamihi container."""


kamihi_container = container(
    image="{kamihi_image.id}",
    ports={"4242/tcp": None},
    environment={
        "KAMIHI_TESTING": "True",
        "KAMIHI_TOKEN": "{test_settings.bot_token}",
        "KAMIHI_LOG__STDOUT_LEVEL": "TRACE",
        "KAMIHI_LOG__STDOUT_SERIALIZE": "True",
        "KAMIHI_DB__HOST": "mongodb://{mongo_container.ips.primary}",
        "KAMIHI_WEB__HOST": "0.0.0.0",
    },
    volumes={
        "{kamihi_volume.name}": {"bind": "/app/src"},
    },
    command="uv run /app/src/main.py",
)
"""Fixture that provides the Kamihi container."""


@pytest.fixture
def wait_for_log(kamihi_container):
    """Fixture that provides a function to wait for specific logs in the Kamihi container."""

    def _wait_for_log(level: str, message: str, timeout: int = 5) -> dict:
        """
        Wait for a specific log entry in the Kamihi container.

        This function will check the logs of the Kamihi container for a specific log entry
        with the given level and message. It will keep checking until the log entry is found
        or the timeout is reached.

        Args:
            level (str): The log level to wait for (e.g., "INFO", "ERROR").
            message (str): The message to wait for in the log entry.
            timeout (int): The maximum time to wait for the log entry (in seconds).

        Returns:
            dict: The log entry that matches the specified level and message.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            for line in kamihi_container.logs().split("\n"):
                try:
                    log_entry = json.loads(line.strip())
                    if isinstance(log_entry, dict) and "record" in log_entry:
                        # Check if the log entry matches the expected level and message
                        if log_entry["record"]["level"]["name"] == level and message in log_entry["record"]["message"]:
                            return log_entry
                except json.JSONDecodeError:
                    pass
            time.sleep(0.1)
        raise TimeoutError(f"Timeout waiting for {level} log with message '{message}' after {timeout} seconds.")

    return _wait_for_log


@pytest.fixture
def kamihi(kamihi_container: Container, wait_for_log, request) -> Generator[Container, Any, None]:
    """Fixture that provides the Kamihi container after ensuring it is ready."""
    wait_for_log("SUCCESS", "Started!")

    yield kamihi_container

    test_results_path = Path.cwd() / "test-results" / "logs"
    test_results_path.mkdir(parents=True, exist_ok=True)
    test_name = request.node.module.__name__ + "." + request.node.name
    test_name = Path(
        test_name.replace("tests.functional", str(test_results_path) + "/functional")
        .replace(".", "/")
        .replace(":", "/")
    )
    test_name.parent.mkdir(parents=True, exist_ok=True)
    with open(test_name.with_suffix(".log"), "w") as log_file:
        log_file.write(kamihi_container.logs())


@pytest.fixture
async def admin_page(kamihi: Container, wait_for_log, page) -> Page:
    """Fixture that provides the admin page of the Kamihi web interface."""
    wait_for_log("TRACE", "Uvicorn running on http://0.0.0.0:4242 (Press CTRL+C to quit)")
    await page.goto(f"http://127.0.0.1:{kamihi.ports['4242/tcp'][0]}/")
    return page


@pytest.fixture(autouse=True)
def mongodb(kamihi: Container, mongo_container: Container) -> Generator[None, Any, None]:
    """Fixture that provides the MongoDB container."""
    connect(host=f"mongodb://{mongo_container.ips.primary}/kamihi", alias="default")

    yield

    disconnect()


@pytest.fixture
async def user_in_db(kamihi: Container, test_settings):
    """Fixture that creates a user in the MongoDB database."""
    user = User(telegram_id=test_settings.user_id, is_admin=False).save()

    yield user

    user.delete()


@pytest.fixture
async def add_permission_for_user(kamihi: Container, test_settings):
    """Fixture that returns a function to add permissions to a user for an action in the MongoDB database."""

    def _add_permission(user: User, action_name: str):
        action = RegisteredAction.objects(name=action_name).first()
        Permission(action=action, users=[user], roles=[]).save()

    yield _add_permission
