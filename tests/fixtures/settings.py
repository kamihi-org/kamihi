"""
Testing settings.

License:
    MIT

"""
from ipaddress import IPv4Address
from typing import Any, Generator

import pytest
import redis
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource
from redis import Redis


class RedisSettings(BaseSettings):
    """
    Settings for Redis connection.

    Attributes:
        host (str): The Redis host.
        port (int): The Redis port.
        password (str | None): The Redis password.

    """

    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: str | None = Field(default=None)

    pool_list: str = Field(default="tg")
    in_use_list: str = Field(default="tg_lock")

    prefix_lock: str = Field(default="lock:")
    prefix_flood: str = Field(default="flood:")

    lease_ttl: int = Field(default=3600)
    retries: int = Field(default=40)
    retry_delay: float = Field(default=0.5)


class TestingSettings(BaseSettings):
    """
    Settings for the testing environment.

    Attributes:
        api_id (int): The API ID.
        api_hash (str): The API hash.
        dc_id (int): The data center ID.
        dc_ip (str): The data center IP address.
        redis (RedisSettings): Redis connection settings.

    """

    api_id: int = Field()
    api_hash: str = Field()
    dc_id: int = Field()
    dc_ip: IPv4Address = Field()
    redis: RedisSettings = Field(default_factory=RedisSettings)
    validation_retries: int = Field(default=5)

    model_config = SettingsConfigDict(
        env_prefix="KAMIHI_TESTING__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
        yaml_file="testing.yml",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # skipcq: PYL-W0621
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize the order of settings sources.

        This method allows you to customize the order in which settings sources are
        loaded. The order of sources is important because it determines which settings
        take precedence when there are conflicts.
        The order of sources is as follows:
            1. Environment variables
            2. .env file
            3. YAML file
            4. Initial settings

        Args:
            settings_cls: the settings class to customize sources for
            init_settings: settings from class initialization
            env_settings: settings from environment variables
            dotenv_settings: settings from .env file
            file_secret_settings: settings from file secrets

        Returns:
            tuple: A tuple containing the customized settings sources in the desired order.

        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(
                settings_cls,
                yaml_file="testing.yml",
            ),
            file_secret_settings,
        )


@pytest.fixture(scope="session")
def test_settings(request, worker_id) -> Generator[TestingSettings, Any, None]:
    """
    Fixture to provide the testing settings.

    Returns:
        TestingSettings: The testing settings.

    """
    setts = TestingSettings()
    yield setts


@pytest.fixture(scope="session")
def redis_client(test_settings) -> Generator[Redis, Any, None]:
    """
    Fixture to provide a Redis client for the testing environment.

    Returns:
        Redis: The Redis client for the testing environment.

    """
    r = redis.Redis(
        host=test_settings.redis.host,
        port=test_settings.redis.port,
        password=test_settings.redis.password,
        decode_responses=False
    )
    yield r
    r.close()
