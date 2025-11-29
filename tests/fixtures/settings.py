"""
Testing settings.

License:
    MIT

"""
from ipaddress import IPv4Address

import pytest
from pydantic import Field, BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource


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
    phone_number: str = PhoneNumber()
    user_id: int = Field()
    bot_token: str = Field()
    bot_username: str = Field()
    session: str = Field()


class TestingSettings(BaseSettings):
    """
    Settings for the testing environment.

    Attributes:
        api_id (int): The API ID.
        api_hash (str): The API hash.
        dc_id (int): The data center ID.
        dc_ip (str): The data center IP address.
        wait_time (float): The wait time between requests.
        credentials (list[Credentials]): List of credential sets for testing.

    """

    api_id: int = Field()
    api_hash: str = Field()
    dc_id: int = Field()
    dc_ip: IPv4Address = Field()
    wait_time: float = Field(default=0.5)
    credentials: Credentials | list[Credentials] = Field(default_factory=list)

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
def test_settings(request, worker_id) -> TestingSettings:
    """
    Fixture to provide the testing settings.

    Returns:
        TestingSettings: The testing settings.

    """
    global_setts = TestingSettings()
    setts = TestingSettings()
    if worker_id == "master":
        setts.credentials = global_setts.credentials[0]
    else:
        setts.credentials = global_setts.credentials[int(worker_id.replace("gw", ""))]
    return setts
