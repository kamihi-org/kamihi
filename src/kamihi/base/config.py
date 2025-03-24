"""
Configuration module.

This module contains the configuration settings for the Kamihi framework. The configuration settings are loaded from
environment variables and/or a `.env` file. They must begin with the prefix `KAMIHI_`.

License:
    MIT

"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_LEVEL_PATTERN = r"^(TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR|CRITICAL)$"


class LogSettings(BaseModel):
    """
    Defines the logging configuration schema.

    Attributes:
        log_level (str): The logging level for the application.

    """

    stdout_enable: bool = Field(default=True)
    stdout_level: str = Field(default="INFO", pattern=_LEVEL_PATTERN)
    stderr_enable: bool = Field(default=False)
    stderr_level: str = Field(default="ERROR", pattern=_LEVEL_PATTERN)
    file_enable: bool = Field(default=False)
    file_level: str = Field(default="DEBUG", pattern=_LEVEL_PATTERN)
    file_path: str = Field(default="kamihi.log")
    notification_enable: bool = Field(default=False)
    notification_level: str = Field(default="SUCCESS", pattern=_LEVEL_PATTERN)
    notification_urls: list[str] = Field(default_factory=list)


class KamihiSettings(BaseSettings):
    """
    Defines the configuration schema for the Kamihi framework.

    Attributes:
        model_config (SettingsConfigDict): Configuration dictionary for environment settings.

    """

    log: LogSettings = Field(default_factory=LogSettings)

    model_config = SettingsConfigDict(
        env_prefix="KAMIHI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
