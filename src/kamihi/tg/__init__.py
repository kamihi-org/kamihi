"""
Telegram module for Kamihi.

This module provides the communication with the Telegram API

License:
    MIT

"""

from .client import TelegramClient
from .send import send

__all__ = ["TelegramClient", "send"]
