"""
Fixtures for Telegram client and chat conversation using Telethon.

License:
    MIT

"""

from __future__ import annotations

import base64
import json
import time

from typing import AsyncGenerator, Any

import pytest
from pydantic import BaseModel, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from redis import Redis
from telegram.error import TelegramError
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation

from tests.fixtures.settings import TestingSettings


class Credentials(BaseModel):
    """
    Credential set for the testing environment

    Attributes:
        session (str): The session string.
        phone_number (str): The phone number.
        user_id (int): The user ID.
        bot_token (str): The bot token.
        bot_username (str): The bot username.
    """

    settings: TestingSettings = Field(exclude=True)
    key: str = Field(exclude=True)

    phone_number: str = PhoneNumber()
    user_id: int = Field()
    bot_token: str = Field()
    bot_username: str = Field()
    session: str = Field()

    _client: TelegramClient | None = None

    @classmethod
    def from_base64(cls, test_settings: TestingSettings, key: str) -> "Credentials | None":
        """Decode the credentials from base64 encoding."""
        if not key:
            return None

        try:
            creds = cls(**json.loads(base64.b64decode(key)), settings=test_settings, key=key)
            return creds
        except Exception as e:
            print(f"Decode error: {e}")
            return None

    async def connect(self) -> None:
        """Connect the Telegram client."""
        if self._client and self.client.is_connected():
            return

        self._client = TelegramClient(
            StringSession(self.session),
            self.settings.api_id,
            self.settings.api_hash,
            sequential_updates=True,
        )
        self._client.session.set_dc(
            self.settings.dc_id,
            str(self.settings.dc_ip),
            443,
        )
        await self._client.connect()
        await self._client.sign_in(phone=self.phone_number)

    async def test(self) -> int:
        """
        Test if the credentials are valid by fetching the user info.

        Returns:
            int: 0 if valid, number of seconds to wait if rate limited, 3600 if invalid.
        """
        await self.connect()
        try:
            _ = await self._client.get_me()
            return 0
        except FloodWaitError as e:
            return e.seconds
        except TelegramError:
            return 3600

    @property
    def client(self) -> TelegramClient:
        """Get the Telegram client."""
        if not self._client:
            raise RuntimeError("Client not connected")
        return self._client


def _checkout_key(test_settings: TestingSettings, redis_client: Redis) -> str | None:
    """
    Checkout a key from the Redis pool.

    Args:
        test_settings (TestingSettings): The testing settings.
        redis_client (Redis): The Redis client.

    Returns:
        str | None: The checked out key or None if no key is available.
    """
    key = None
    for _ in range(test_settings.redis.retries):
        key_bytes = redis_client.rpoplpush(test_settings.redis.pool_list, test_settings.redis.in_use_list)

        if key_bytes:
            key = key_bytes.decode("utf-8")
            if redis_client.exists(f"{test_settings.redis.prefix_flood}{key}"):
                redis_client.lrem(test_settings.redis.in_use_list, 1, key)
                redis_client.lpush(test_settings.redis.pool_list, key)
                continue

            lock_key = f"{test_settings.redis.prefix_lock}{key}"
            if redis_client.set(lock_key, "1", nx=True, ex=test_settings.redis.lease_ttl):
                break

            redis_client.lrem(test_settings.redis.in_use_list, 1, key)
            redis_client.lpush(test_settings.redis.pool_list, key)

        time.sleep(test_settings.redis.retry_delay)

    return key


def _checkin_key(test_settings: TestingSettings, redis_client: Redis, key: str, cooldown_seconds: int = 0) -> None:
    """
    Returns a raw key string to the pool.

    Args:
        test_settings (TestingSettings): The testing settings.
        redis_client (Redis): The Redis client.
        key (str): The key to return.
        cooldown_seconds (int): The cooldown period in seconds before the key can be checked out again

    Returns:
        None
    """
    if not key:
        return

    if cooldown_seconds > 0:
        redis_client.set(f"{test_settings.redis.prefix_flood}{key}", "1", ex=cooldown_seconds)

    redis_client.delete(f"{test_settings.redis.prefix_lock}{key}")
    redis_client.lrem(test_settings.redis.in_use_list, 1, key)
    redis_client.lpush(test_settings.redis.pool_list, key)


@pytest.fixture
async def credentials(test_settings, request, redis_client: Redis) -> AsyncGenerator[Credentials, Any]:
    """
    Fixture to provide the credentials for the testing environment.

    Returns:
        Credentials: The credentials for the testing environment.

    """
    cred = None
    for _ in range(test_settings.validation_retries):
        key = _checkout_key(test_settings, redis_client)
        cred = Credentials.from_base64(test_settings, key)

        await cred.connect()
        cooldown = await cred.test()

        if cooldown == 0:
            break
        else:
            _checkin_key(test_settings, redis_client, key, cooldown)

    if not cred:
        raise RuntimeError("No available API keys (all in use or cooling down)")

    try:
        yield cred
    finally:
        cooldown = await cred.test()
        _checkin_key(test_settings, redis_client, cred.key, cooldown)


@pytest.fixture
async def tg_client(credentials: Credentials) -> AsyncGenerator[TelegramClient, Any]:
    """Create and connect a Telegram client."""
    await credentials.connect()
    yield credentials.client


@pytest.fixture
async def chat(tg_client: TelegramClient, credentials: Credentials) -> AsyncGenerator[Conversation, Any]:
    """Open conversation with the bot."""
    async with tg_client.conversation(credentials.bot_username, timeout=60, max_messages=10000) as conv:
        yield conv
