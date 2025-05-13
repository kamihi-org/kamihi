"""
Bot module for Kamihi.

This module provides the primary interface for the Kamihi framework, allowing
for the creation and management of Telegram bots.

License:
    MIT

"""

from .action import Action
from .bot import Bot

__all__ = ["Bot", "Action"]
