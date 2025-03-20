"""
Configuration module.

This module contains the configuration settings for the Kamihi framework. The configuration settings are loaded from
environment variables and/or a `.env` file. They must begin with the prefix `KAMIHI_`.

License:
    MIT

"""

from pydantic import BaseModel


class KamihiSettings(BaseModel):
    """Defines the configuration schema for the Kamihi framework."""

    pass
