"""
Logging configuration module.

This module provides functions to configure logging for the Kamihi framework.

License:
    MIT

Examples:
    >>> from kamihi.base.logging import configure_logging
    >>> from kamihi.base.config import LogSettings
    >>> from loguru import logger
    >>> settings = LogSettings()
    >>> configure_logging(logger, settings)
    >>> logger.info("This is an info message.")

"""

from __future__ import annotations

import inspect
import logging
import sys

import loguru

from .config import LogSettings
from .manual_send import ManualSender


def _extra_formatter(record: loguru.Record) -> None:
    """
    Add a compact representation of the extra fields to the log record.

    This function takes a log record and adds the extra fields in a compact
    way and only if there are any.

    Args:
        record: The log record to format.

    """
    if record.get("extra"):
        record["extra"]["compact"] = ", ".join(
            f"{key}={repr(value)}" for key, value in record["extra"].items() if key != "compact"
        )


class _InterceptHandler(logging.Handler):
    def __init__(
        self, logger: loguru.Logger, include: list[str] | None = None, exclude: list[str] | None = None
    ) -> None:
        super().__init__()
        self.logger = logger
        self.include = include or []
        self.exclude = exclude or []

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        Args:
            record: The log record to emit.

        """
        logger_name = record.name

        if any(logger_name.startswith(mod) for mod in self.exclude):
            return

        if self.include and not any(logger_name.startswith(mod) for mod in self.include):
            return

        try:
            level = self.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        self.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


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

    logger.configure(patcher=_extra_formatter, extra={"compact": ""})

    if settings.stdout_enable:
        logger.add(
            sys.__stdout__,
            level=settings.stdout_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{message} "
            "<dim>{extra[compact]}</dim>",
            serialize=settings.stdout_serialize,
            enqueue=True,
        )

    if settings.stderr_enable:
        logger.add(
            sys.__stderr__,
            level=settings.stderr_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{message} "
            "<dim>{extra[compact]}</dim>",
            serialize=settings.stderr_serialize,
            enqueue=True,
        )

    if settings.file_enable:
        logger.add(
            settings.file_path,
            level=settings.file_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{message} "
            "<dim>{extra[compact]}</dim>",
            serialize=settings.file_serialize,
            rotation=settings.file_rotation,
            retention=settings.file_retention,
            enqueue=True,
        )

    if settings.notification_enable:
        manual_sender = ManualSender(settings.notification_urls)
        logger.add(
            manual_sender.notify,
            level=settings.notification_level,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{message} "
            "<dim>{extra[compact]}</dim>",
            filter={"apprise": False},
            enqueue=True,
        )

    logging.basicConfig(
        handlers=[_InterceptHandler(logger, include=["alembic"])],
        level=0,
        force=True,
    )


class StreamToLogger:
    """
    Fake file-like stream object that redirects writes to a logger instance.

    Args:
        logger: The logger instance to redirect writes to.
        level: The log level to use for the writes (default: "INFO").

    """

    def __init__(self, logger: loguru.Logger, level: str = "INFO") -> None:
        """
        Initialize the stream to logger.

        Args:
            logger: The logger instance to redirect writes to.
            level: The log level to use for the writes (default: "INFO").

        """
        self.logger = logger
        self._level = level

    def write(self, buffer: str) -> None:
        """
        Write a buffer to the logger.

        Args:
            buffer: The buffer to write.

        """
        for line in buffer.rstrip().splitlines():
            self.logger.opt(depth=1).log(self._level, line.strip())

    def flush(self) -> None:
        """Flush the stream."""
        pass
