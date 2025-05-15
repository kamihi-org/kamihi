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
from textwrap import dedent
from typing import Any, AsyncGenerator
from unittest import mock

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

from pytest_docker_tools import build, container, image, fetch, volume, fxtr

load_dotenv()

BOT_TOKEN = os.getenv("KAMIHI_TESTING__BOT_TOKEN")
BOT_USERNAME = os.getenv("KAMIHI_TESTING__BOT_USERNAME")
USER_ID = int(os.getenv("KAMIHI_TESTING__USER_ID"))
PHONE_NUMBER = os.getenv("KAMIHI_TESTING__TG_PHONE_NUMBER")
API_ID = int(os.getenv("KAMIHI_TESTING__TG_API_ID"))
API_HASH = os.getenv("KAMIHI_TESTING__TG_API_HASH")
SESSION = os.getenv("KAMIHI_TESTING__TG_SESSION")
DC_ID = int(os.getenv("KAMIHI_TESTING__TG_DC_ID"))
DC_IP = os.getenv("KAMIHI_TESTING__TG_DC_IP")
WAIT_TIME = int(os.getenv("KAMIHI_TESTING__WAIT_TIME", 0.5))


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
def wait_for_log(kamihi_container):
    def _wait_for_log(level: str, message: str, timeout: int = 5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
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
            except FileNotFoundError:
                pass

            time.sleep(0.1)

        raise TimeoutError(f"Timeout waiting for {level} log with message '{message}' after {timeout} seconds.")

    return _wait_for_log


@pytest.fixture
def user_code():
    return {
        "main.py": dedent("""
                         from kamihi import bot
                         bot.start()
                         """).encode()
    }


mongo_image = fetch(repository="mongo:latest")


mongo = container(
    image="{mongo_image.id}",
)


kamihi_image = build(path=".", dockerfile="tests/integration/docker/Dockerfile")


kamihi_volume = volume(initial_content=fxtr("user_code"))


kamihi_container = container(
    image="{kamihi_image.id}",
    ports={"4242/tcp": None},
    environment={
        "KAMIHI_TESTING": "True",
        "KAMIHI_TOKEN": BOT_TOKEN,
        "KAMIHI_LOG__STDOUT_LEVEL": "TRACE",
        "KAMIHI_LOG__STDOUT_SERIALIZE": "True",
        "KAMIHI_DB__HOST": "mongodb://{mongo.ips.primary}",
    },
    volumes={
        "{kamihi_volume.name}": {"bind": "/app/src"},
    },
    command="uv run /app/src/main.py",
)


@pytest.fixture
def kamihi(kamihi_container, wait_for_log):
    wait_for_log("SUCCESS", "Started!")
    return kamihi_container
