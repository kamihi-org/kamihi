"""
Utility functions and variables for the Kamihi project.

License:
    MIT
"""

import functools
import importlib
import re
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from telegram.constants import BotCommandLimit

if TYPE_CHECKING:
    from loguru import Logger  # skipcq: TCV-001

COMMAND_REGEX = re.compile(rf"^[a-z0-9_]{{{BotCommandLimit.MIN_COMMAND},{BotCommandLimit.MAX_COMMAND}}}$")
UUID4_REGEX = re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}")


@functools.cache
def _check_extra_installed(group: str) -> None:
    """Check if all dependencies of a given extra are installed (cached)."""
    try:
        reqs = importlib.metadata.requires("kamihi")
    except importlib.metadata.PackageNotFoundError:
        reqs = []

    extra_marker = f"extra == '{group}'"
    deps = [req.split(";")[0].strip() for req in reqs if extra_marker in req]

    for dep in deps:
        pkg = dep.split()[0].split(">=")[0].split("==")[0].split("[")[0]
        try:
            importlib.metadata.distribution(pkg)
        except importlib.metadata.PackageNotFoundError as e:
            msg = (
                f"Missing required optional dependency '{pkg}' for group '{group}'. "
                f"Please run 'uv add kamihi[{group}]' to install."
            )
            raise ImportError(msg) from e


def requires(group: str) -> Callable:
    """
    Check if required optional dependencies are available.

    Args:
        group (str): The name of the extra group to check for dependencies.

    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _check_extra_installed(group)
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def timer(logger: "Logger", message: str, level: str = "DEBUG") -> Generator[None, Any, None]:  # noqa: ANN001
    """
    Context manager to log the time taken for a block of code.

    Args:
        logger (Logger): The logger instance to use for logging.
        message (str): The message to log with the elapsed time.
        level (str): The logging level to use (default is "DEBUG").

    Returns:
        Generator[None, Any, None]: A generator that yields control to the block of code being timed.

    """
    start_time = time.perf_counter()
    yield
    end_time = time.perf_counter()
    logger.bind(ms=round((end_time - start_time) * 1000)).log(level, message)


@functools.lru_cache(maxsize=1)
def cron_regex() -> re.Pattern:
    """
    Get the compiled regex pattern for validating cron expressions.

    Returns:
        re.Pattern: The compiled regex pattern.

    """
    # Month and weekday names
    month_name = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    weekday_name = r"(?:mon|tue|wed|thu|fri|sat|sun)"
    name = rf"(?:{month_name}|{weekday_name})"

    # Basic building blocks
    number = r"\d+"
    star = r"\*"
    step = rf"(?:\*/{number})"
    rng = rf"(?:{number}|{name})-(?:{number}|{name})"
    rng_step = rf"{rng}/{number}"
    xth_y = rf"{number}th\s+(?:{number}|{weekday_name})"
    last_x = rf"last\s+(?:{number}|{weekday_name})"
    last = r"last"

    # Single field expression
    single_expr = rf"(?:{star}|{step}|{rng_step}|{rng}|{number}|{name}|{xth_y}|{last_x}|{last})"

    # Comma-separated list
    field = rf"{single_expr}(?:,{single_expr})*"

    # Full crontab line (5–7 fields)
    return re.compile(
        rf"^(?:{field}\s+){{4,6}}{field}$",  # 5–7 fields
        re.IGNORECASE,
    )


def is_valid_cron_expression(expression: str) -> bool:
    """
    Validate if a given string is a valid cron expression.

    Args:
        expression (str): The cron expression to validate.

    Returns:
        bool: True if the expression is valid, False otherwise.

    """
    return bool(cron_regex().match(expression.strip()))
