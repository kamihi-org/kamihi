"""
Configuration module.

This module contains the configuration settings for the Kamihi framework. The configuration settings are loaded from
environment variables and/or a `.env` file. They must begin with the prefix `KAMIHI_`.

License:
    MIT

Attributes:
    settings (KamihiSettings): Global instance of settings.

"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class KamihiSettings(BaseSettings):
    """
    Defines the configuration schema for the Kamihi framework.

    Attributes:
        model_config (SettingsConfigDict): Configuration dictionary for environment settings.

    """

    model_config = SettingsConfigDict(
        env_prefix="KAMIHI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global instance of settings
settings = KamihiSettings()


def get_settings() -> KamihiSettings:
    """
    Get the current settings.

    This function returns the current settings object, which can be used
    to access or modify configuration options.

    Returns:
       KamihiSettings: The current settings object.

    """
    return settings
