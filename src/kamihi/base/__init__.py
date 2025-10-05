"""
Base module for the Kamihi framework.

Provides base utilities and classes for the framework.

License:
    MIT

"""

from .config import KamihiSettings, get_settings, init_settings
from .logging import configure_logging

__all__ = ["KamihiSettings", "get_settings", "init_settings", "configure_logging"]
