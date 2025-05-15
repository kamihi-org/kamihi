"""
Common fixtures for functional tests.

License:
    MIT

"""

import json
import time
from textwrap import dedent
from typing import Any, AsyncGenerator

import pytest
from dotenv import load_dotenv
from playwright.async_api import Page
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytest_docker_tools.wrappers import Container
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation

from pytest_docker_tools import build, container, fetch, volume, fxtr


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
async def conversation(test_settings, tg_client) -> AsyncGenerator[Conversation, Any]:
    """Open conversation with the bot."""
    async with tg_client.conversation(test_settings.bot_username, timeout=10, max_messages=10000) as conv:
        conv: Conversation

        await conv.send_message("/start")
        await conv.get_response()  # Welcome message
        time.sleep(0.5)
        yield conv


@pytest.fixture
def user_code():
    """Fixture to provide the user code for the bot."""
    return {
        "main.py": dedent("""
                         from kamihi import bot
                         bot.start()
                         """).encode()
    }


mongo_image = fetch(repository="mongo:latest")
"""Fixture that fetches the mongodb container image."""


mongo = container(
    name="kamihi_test_mongo",
    image="{mongo_image.id}",
)
"""Fixture that provides the mongodb container."""


kamihi_image = build(path=".", dockerfile="tests/functional/docker/Dockerfile")
"""Fixture that builds the kamihi container image."""


kamihi_volume = volume(initial_content=fxtr("user_code"), name="kamihi_test_volume")
"""Fixture that creates a volume for the kamihi container."""


kamihi_container = container(
    name="kamihi_test",
    image="{kamihi_image.id}",
    ports={"4242/tcp": None},
    environment={
        "KAMIHI_TESTING": "True",
        "KAMIHI_TOKEN": "{test_settings.bot_token}",
        "KAMIHI_LOG__STDOUT_LEVEL": "TRACE",
        "KAMIHI_LOG__STDOUT_SERIALIZE": "True",
        "KAMIHI_DB__HOST": "mongodb://{mongo.ips.primary}",
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
                        if (
                            log_entry["record"]["level"]["name"] == level
                            and message in log_entry["record"]["message"]
                        ):
                            return log_entry
                except json.JSONDecodeError:
                    pass
            time.sleep(0.1)
        raise TimeoutError(f"Timeout waiting for {level} log with message '{message}' after {timeout} seconds.")
    return _wait_for_log


@pytest.fixture
def kamihi(kamihi_container: Container, wait_for_log) -> Container:
    """Fixture that provides the Kamihi container after ensuring it is ready."""
    wait_for_log("SUCCESS", "Started!")
    return kamihi_container


@pytest.fixture
async def admin_page(kamihi: Container, wait_for_log, page) -> Page:
    """Fixture that provides the admin page of the Kamihi web interface."""
    wait_for_log("TRACE", "Uvicorn running on http://0.0.0.0:4242 (Press CTRL+C to quit)")
    await page.goto(f"http://127.0.0.1:{kamihi.ports['4242/tcp'][0]}/")
    return page
