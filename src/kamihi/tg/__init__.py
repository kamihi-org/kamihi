"""
Telegram module for Kamihi.

This module provides the communication with the Telegram API

License:
    MIT

"""

from .client import TelegramClient
from .send import reply_text, send_text

__all__ = ["TelegramClient", "reply_text", "send_text"]
