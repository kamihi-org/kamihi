"""
Utilities and constants for the bot module.

License:
    MIT

Attributes:
    COMMAND_REGEX (re.Pattern): Regular expression pattern for validating command names.

"""

import re
from typing import Annotated, Any, get_args, get_origin

from telegram.constants import BotCommandLimit

COMMAND_REGEX = re.compile(rf"^[a-z0-9_]{{{BotCommandLimit.MIN_COMMAND},{BotCommandLimit.MAX_COMMAND}}}$")


def parse_annotation(ann: Any) -> tuple[type, Any]:  # noqa: ANN401
    """
    Parse an annotation, extracting base type and metadata.

    Args:
        ann (Any): The annotation to parse.

    Returns:
        tuple: A tuple containing the base type and metadata.

    """
    origin = get_origin(ann)
    if origin is Annotated:
        args = get_args(ann)
        base_type = args[0]
        metadata = args[1]
        return base_type, metadata
    return ann, None
