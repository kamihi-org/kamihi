"""
Configuration module.

This module contains the configuration settings for the Kamihi framework. The configuration settings are loaded from
environment variables and/or a `.env` file. They must begin with the prefix `KAMIHI_`.

License:
    MIT

"""

import os
import re

import pytz
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from pytz.tzinfo import DstTzInfo

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
    stdout_level: str = Field(default="INFO")
    stdout_serialize: bool = Field(default=False)

    stderr_enable: bool = Field(default=False)
    stderr_level: str = Field(default="ERROR")
    stderr_serialize: bool = Field(default=False)

    file_enable: bool = Field(default=False)
    file_level: str = Field(default="DEBUG")
    file_path: str = Field(default="kamihi.log")
    file_serialize: bool = Field(default=False)
    file_rotation: str = Field(default="1 MB")
    file_retention: str = Field(default="7 days")

    notification_enable: bool = Field(default=False)
    notification_level: str = Field(default="SUCCESS")
    notification_urls: list[str] = Field(default_factory=list)

    @field_validator("stdout_level", "stderr_level", "file_level", "notification_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """
        Validate the log level value.

        Args:
            value (str): The log level value to validate.

        Returns:
            str: The validated log level value.

        Raises:
            ValueError: If the log level is invalid.

        """
        value = value.upper()

        if not re.match(_LEVEL_PATTERN, value):
            msg = f"Invalid log level: {value}"
            raise ValueError(msg)

        return value


class ResponseSettings(BaseModel):
    """
    Defines the response settings schema.

    Attributes:
        default_enabled(bool): Whether to enable the default message
        default_message(str): The message to return when no handler has been triggered
        error_message(str): The message to send to the user when an error happens

    """

    default_enabled: bool = Field(default=True)
    default_message: str = Field(default="I'm sorry, but I don't know how to respond to that")
    error_message: str = Field(default="An error occurred while processing your request, please try again later")


class WebSettings(BaseModel):
    """
    Defines the web settings schema.

    Attributes:
        secret (str): The secret key for the web server.
        host (str): The host of the web interface.
        port (int): The port of the web interface.

    """

    host: str = Field(default="localhost")
    port: int = Field(default=4242)


class DatabaseSettings(BaseModel):
    """
    Defines the database settings schema.

    Attributes:
        host (str): The URL of the database.
        name (str): The name of the database.

    """

    host: str = Field(
        default="mongodb://localhost:27017",
        pattern=r"^mongodb(\+srv)?://([a-zA-Z0-9_.-]+(:[a-zA-Z0-9_.-]+)?@)?[a-zA-Z0-9_.-]+(:[0-9]{1,5})?$",
    )
    name: str = Field(default="kamihi")


class KamihiSettings(BaseSettings):
    """
    Defines the configuration schema for the Kamihi framework.

    Attributes:
        timezone (str): The timezone for the application.
        autoreload_templates (bool): Whether to enable template auto-reloading.
        log (LogSettings): The logging settings.
        db (DatabaseSettings): The database settings.
        token (str | None): The Telegram bot token.
        responses (ResponseSettings): The response settings.
        web (WebSettings): The web settings.

    """

    # General settings
    testing: bool = Field(default=False)
    timezone: str = Field(default="UTC", validate_default=True)

    # Template settings
    autoreload_templates: bool = Field(default=True)

    # Logging settings
    log: LogSettings = Field(default_factory=LogSettings)

    # Database settings
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Telegram settings
    token: str | None = Field(default=None, pattern=r"^\d+:[0-9A-Za-z_-]{35}$", exclude=True)
    responses: ResponseSettings = Field(default_factory=ResponseSettings)

    # Web settings
    web: WebSettings = Field(default_factory=WebSettings)

    @field_validator("timezone")
    @classmethod
    def _validate_timezone(cls, value: str) -> str:
        """
        Validate the timezone value.

        Args:
            value (str): The timezone value to validate.

        Returns:
            str: The validated timezone value.

        Raises:
            ValueError: If the timezone is invalid.

        """
        if value not in pytz.all_timezones:
            msg = f"Invalid timezone: {value}"
            raise ValueError(msg)

        return value

    @property
    def timezone_obj(self) -> DstTzInfo:
        """
        Get the timezone object.

        Returns:
            DstTzInfo: The timezone object.

        """
        return pytz.timezone(self.timezone)

    model_config = SettingsConfigDict(
        env_prefix="KAMIHI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
        yaml_file="kamihi.yaml",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
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
            YamlConfigSettingsSource(settings_cls, yaml_file=os.getenv("KAMIHI_CONFIG_FILE", "kamihi.yaml")),
            file_secret_settings,
        )
