"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]

"""

from __future__ import annotations

import sys

import loguru

from kamihi.base.config import LogSettings
from kamihi.base.manual_send import ManualSender


def configure_logging(logger: loguru.Logger, settings: LogSettings) -> None:
    """
    Configure logging for the module.

    This function sets up the logging configuration for the module, including
    log level and format.

    Args:
        logger: The logger instance to configure.
        settings: The logging settings to configure.

    """
    logger.remove()

    if settings.stdout_enable:
        logger.add(
            sys.stdout,
            level=settings.stdout_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            serialize=settings.stdout_serialize,
        )

    if settings.stderr_enable:
        logger.add(
            sys.stderr,
            level=settings.stderr_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            serialize=settings.stderr_serialize,
        )

    if settings.file_enable:
        logger.add(
            settings.file_path,
            level=settings.file_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            serialize=settings.file_serialize,
        )

    if settings.notification_enable:
        manual_sender = ManualSender(settings.notification_urls)
        logger.add(
            manual_sender.notify,
            level=settings.notification_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            filter={"apprise": False},
        )
