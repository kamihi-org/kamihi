"""
Fixtures for Telegram client and chat conversation using Telethon.

License:
    MIT

"""

from __future__ import annotations

import base64
import json
import os
import random
import socket
import time
import uuid
from dataclasses import dataclass
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


_CHECKOUT_LUA = """
local lock_key = KEYS[1]
local ready_key = KEYS[2]
local meta_key = KEYS[3]

local member = ARGV[1]
local owner = ARGV[2]
local ttl = tonumber(ARGV[3])
local score = tonumber(ARGV[4])
local now = tonumber(ARGV[5])

local ok = redis.call('SET', lock_key, owner, 'NX', 'EX', ttl)
if not ok then
    redis.call('ZADD', ready_key, score, member)
    return 0
end

redis.call('HSET', meta_key,
    'owner', owner,
    'leased_at', now,
    'lease_expires_at', now + ttl
)
return 1
"""


_CHECKIN_LUA = """
local lock_key = KEYS[1]
local ready_key = KEYS[2]
local meta_key = KEYS[3]

local member = ARGV[1]
local owner = ARGV[2]
local score = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

local current = redis.call('GET', lock_key)
if current and current ~= owner then
    return 0
end

redis.call('DEL', lock_key)
redis.call('ZADD', ready_key, score, member)
redis.call('HSET', meta_key,
    'owner', owner,
    'last_release_at', now,
    'next_available_at', score
)
return 1
"""


@dataclass
class Lease:
    key: str
    ready_at: float


class RedisLeaseManager:
    def __init__(self, settings: TestingSettings, redis_client: Redis):
        self._settings = settings
        self._redis = redis_client
        self._owner_id = f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4()}"
        self._checkout_script = redis_client.register_script(_CHECKOUT_LUA)
        self._checkin_script = redis_client.register_script(_CHECKIN_LUA)
        self._rng = random.Random()

    @property
    def owner_id(self) -> str:
        return self._owner_id

    @property
    def _ready_key(self) -> str:
        return self._settings.redis.ready_zset

    def checkout(self) -> Lease:
        block = self._settings.redis.checkout_block_seconds
        timeout = 0 if block is None else max(int(block), 0)
        while True:
            result = self._redis.bzpopmin(self._ready_key, timeout=timeout)
            if result is None:
                raise RuntimeError("No available credentials")

            _, member, score = result
            key = member.decode("utf-8")
            ready_at = float(score)
            now = time.time()
            lock_key = f"{self._settings.redis.lock_prefix}{key}"
            meta_key = f"{self._settings.redis.meta_prefix}{key}"
            lease_ttl = int(self._settings.redis.lease_ttl)

            success = self._checkout_script(
                keys=[lock_key, self._ready_key, meta_key],
                args=[key, self._owner_id, lease_ttl, ready_at, now],
            )

            if int(success) == 1:
                return Lease(key=key, ready_at=ready_at)

    def checkin(self, lease: Lease, cooldown_seconds: int) -> None:
        now = time.time()
        cooldown = max(int(cooldown_seconds), 0)
        next_ready = now if cooldown == 0 else now + cooldown
        next_ready += self._rng.random() * 0.5
        lock_key = f"{self._settings.redis.lock_prefix}{lease.key}"
        meta_key = f"{self._settings.redis.meta_prefix}{lease.key}"

        result = self._checkin_script(
            keys=[lock_key, self._ready_key, meta_key],
            args=[lease.key, self._owner_id, next_ready, now],
        )

        if int(result) != 1:
            raise RuntimeError(f"Failed to release credential {lease.key}")


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
    _lease: Lease | None = None

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
        if not await self._client.is_user_authorized():
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


@pytest.fixture
async def credentials(test_settings, request, redis_client: Redis) -> AsyncGenerator[Credentials, Any]:
    """
    Fixture to provide the credentials for the testing environment.

    Returns:
        Credentials: The credentials for the testing environment.

    """
    manager = RedisLeaseManager(test_settings, redis_client)
    lease: Lease | None = None
    cred: Credentials | None = None

    for _ in range(test_settings.validation_retries):
        lease = manager.checkout()
        cred = Credentials.from_base64(test_settings, lease.key)

        if not cred:
            manager.checkin(lease, 0)
            lease = None
            continue

        cred._lease = lease
        await cred.connect()
        cooldown = await cred.test()

        if cooldown == 0:
            break

        manager.checkin(lease, cooldown)
        lease = None
        cred = None

    if not cred or not lease:
        raise RuntimeError("No available API credentials")

    try:
        yield cred
    finally:
        if cred._lease:
            cooldown = await cred.test()
            manager.checkin(cred._lease, cooldown)


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
