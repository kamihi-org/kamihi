"""
Fixtures for Telegram client and chat conversation using Telethon.

License:
    MIT

"""

from typing import AsyncGenerator, Any

import pytest
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation


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
