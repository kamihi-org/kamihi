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
        stdout_enable (bool): Enable or disable stdout logging.
        stdout_level (str): Log level for stdout logging.
        stdout_serialize (bool): Enable or disable serialization for stdout logging.

        stderr_enable (bool): Enable or disable stderr logging.
        stderr_level (str): Log level for stderr logging.
        stderr_serialize (bool): Enable or disable serialization for stderr logging.

        file_enable (bool): Enable or disable file logging.
        file_level (str): Log level for file logging.
        file_path (str): Path to the log file.
        file_serialize (bool): Enable or disable serialization for file logging.
        file_rotation (str): Rotation policy for the log file.
        file_retention (str): Retention policy for the log file.

        notification_enable (bool): Enable or disable notification logging.
        notification_level (str): Log level for notification logging.
        notification_urls (list[str]): List of URLs for notification services.

    """

    stdout_enable: bool = Field(default=True)
    stdout_level: str = Field(default="INFO", pattern=_LEVEL_PATTERN)
    stdout_serialize: bool = Field(default=False)

    stderr_enable: bool = Field(default=False)
    stderr_level: str = Field(default="ERROR", pattern=_LEVEL_PATTERN)
    stderr_serialize: bool = Field(default=False)

    file_enable: bool = Field(default=False)
    file_level: str = Field(default="DEBUG", pattern=_LEVEL_PATTERN)
    file_path: str = Field(default="kamihi.log")
    file_serialize: bool = Field(default=False)
    file_rotation: str = Field(default="1 MB")
    file_retention: str = Field(default="7 days")

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
        env_nested_delimiter="__",
    )
