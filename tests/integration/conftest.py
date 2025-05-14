"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]
"""

import json
import multiprocessing
import os
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from tempfile import TemporaryFile, NamedTemporaryFile
from typing import Any, AsyncGenerator
from unittest import mock

import loguru
import mongomock
import pytest
from dotenv import load_dotenv
from mongoengine import connect, disconnect
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation

from kamihi.base.config import LogSettings
from kamihi.bot import Bot
from kamihi.bot.models import RegisteredAction

load_dotenv()

BOT_USERNAME = os.getenv("KAMIHI_TESTING__BOT_USERNAME")
USER_ID = int(os.getenv("KAMIHI_TESTING__USER_ID"))
PHONE_NUMBER = os.getenv("KAMIHI_TESTING__TG_PHONE_NUMBER")
API_ID = int(os.getenv("KAMIHI_TESTING__TG_API_ID"))
API_HASH = os.getenv("KAMIHI_TESTING__TG_API_HASH")
SESSION = os.getenv("KAMIHI_TESTING__TG_SESSION")
DC_ID = int(os.getenv("KAMIHI_TESTING__TG_DC_ID"))
DC_IP = os.getenv("KAMIHI_TESTING__TG_DC_IP")
WAIT_TIME = int(os.getenv("KAMIHI_TESTING__WAIT_TIME", 0.5))


@pytest.fixture(scope="session", autouse=True)
def mock_mongodb():
    """Fixture to provide a mock MongoDB instance."""
    connect("kamihi_test", host="mongodb://localhost", alias="default", mongo_client_class=mongomock.MongoClient)
    with mock.patch("kamihi.bot.bot.connect"), mock.patch("kamihi.db.mongo.connect"):
        yield
    disconnect()


@pytest.fixture(scope="session")
def bot_username():
    """Fixture to provide the bot username."""
    return BOT_USERNAME


@pytest.fixture(scope="session")
def test_user_id():
    """Fixture to provide a test user ID."""
    return USER_ID


@pytest.fixture(scope="session")
async def tg_client():
    """Fixture to create a test Telegram client for the application."""
    load_dotenv()

    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH, sequential_updates=True)
    client.session.set_dc(
        DC_ID,
        DC_IP,
        443,
    )
    await client.connect()
    await client.sign_in(phone=PHONE_NUMBER)

    yield client

    await client.disconnect()
    await client.disconnected


@pytest.fixture(scope="session")
async def conversation(tg_client) -> AsyncGenerator[Conversation, Any]:
    """Open conversation with the bot."""
    async with tg_client.conversation(BOT_USERNAME, timeout=10, max_messages=10000) as conv:
        conv: Conversation

        await conv.send_message("/start")
        await conv.get_response()  # Welcome message
        time.sleep(0.5)
        yield conv


@pytest.fixture
def temp_path():
    """Fixture to create a temporary file."""
    with NamedTemporaryFile(delete=False) as temp_file:
        yield temp_file.name
    os.remove(temp_file.name)


@pytest.fixture
def wait_for_log_entry(temp_path):
    """
    A pytest fixture that returns a function to wait for a specific JSON log entry
    to be written to a given file path within a timeout.

    Args:
        temp_path: A pytest fixture providing a temporary directory path.

    Returns:
        A callable function with the signature:
        `def _wait_for_log(log_file_path: str, expected_log: dict, timeout: int = 5)`
    """

    def _wait_for_log(level: str, message: str, timeout: int = 5):
        """
        Waits for a specific JSON log entry to appear in the given log file.

        Args:
            expected_log: A dictionary representing the log entry to wait for.
            timeout: The maximum time to wait in seconds (default is 5).

        Raises:
            TimeoutError: If the expected log entry is not found within the timeout.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with open(temp_path, "r") as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            if (
                                log_entry["record"]["level"]["name"] == level
                                and message in log_entry["record"]["message"]
                            ):
                                return log_entry
                        except json.JSONDecodeError:
                            # Handle potential non-JSON lines or incomplete writes
                            pass
            except FileNotFoundError:
                pass  # File might not exist yet

            time.sleep(0.1)  # Wait a bit before checking again

        raise TimeoutError(f"Timeout waiting for {level} log with message '{message}' after {timeout} seconds.")

    return _wait_for_log


@pytest.fixture
def run_bot(temp_path):
    """Fixture that returns a function that can be used to start the bot in another thread."""

    def _start_bot(configure_function: Callable[[Bot], Bot]):
        connect("kamihi_test", host="mongodb://localhost", alias="default", mongo_client_class=mongomock.MongoClient)
        with (
            mock.patch("kamihi.bot.bot.connect"),
            mock.patch("kamihi.db.mongo.connect"),
            mock.patch("kamihi.web.web.connect"),
        ):
            from loguru import logger

            from kamihi import __version__, KamihiSettings
            from kamihi.base.logging import configure_logging

            settings = KamihiSettings(
                log=LogSettings(
                    stdout_level="TRACE", file_enable=True, file_level="TRACE", file_path=temp_path, file_serialize=True
                )
            )
            configure_logging(logger, settings.log)
            logger.trace("Initialized settings and logging")
            logger.bind(version=__version__ + "-test").info("Starting Kamihi")

            # Initialize the bot
            bot_instance = Bot(settings)

            bot_instance = configure_function(bot_instance)

            bot_instance.start()
        disconnect()

    @contextmanager
    def _contextmanager(configure_function: Callable[[Bot], [Bot]]):
        thread = multiprocessing.Process(target=_start_bot, args=(configure_function,), daemon=True)
        thread.start()

        yield

        thread.terminate()
        thread.join()

    return _contextmanager


@pytest.fixture
def create_user():
    """Fixture to create a user in the database."""
    from kamihi.users.models import User

    def _create_user(telegram_id: int, is_admin: bool = False):
        user = User(
            telegram_id=telegram_id,
            is_admin=is_admin,
        )
        user.save()
        return user

    return _create_user


@pytest.fixture
def create_permission_for_user():
    """Fixture to create a permission in the database."""
    from kamihi.users.models import Permission, User

    def _create_permission(action_name: str, user: User):
        permission = Permission(
            action=RegisteredAction.objects(name=action_name).first(),
            users=[user],
            roles=[],
        )
        permission.save()
        return permission

    return _create_permission
