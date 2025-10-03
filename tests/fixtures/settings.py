"""
Testing settings.

License:
    MIT

"""

import pytest
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
