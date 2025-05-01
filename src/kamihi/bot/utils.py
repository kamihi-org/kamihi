"""
Utilities and constants for the bot module.

License:
    MIT

Attributes:
    COMMAND_REGEX (re.Pattern): Regular expression pattern for validating command names.

"""

import re

from telegram.constants import BotCommandLimit

COMMAND_REGEX = re.compile(rf"^[a-z0-9_]{{{BotCommandLimit.MIN_COMMAND},{BotCommandLimit.MAX_COMMAND}}}$")
