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
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
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
