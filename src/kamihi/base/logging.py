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

import sys


def configure_logging() -> None:
    """
    Configure logging for the module.

    This function sets up the logging configuration for the module, including
    log level and format.

    """
    from loguru import logger

    logger.remove()
    handlers = {
        "console": {
            "sink": sys.stderr,
            "level": "INFO",
            "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}:{function}:{line}</cyan> | "
            "<level>{message}</level>",
        },
        "file": {
            "sink": "kamihi.log",
            "level": "DEBUG",
            "serialize": True,
            "rotation": "1 MB",
            "retention": "10 days",
            "compression": "zip",
            "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}:{function}:{line}</cyan> | "
            "<level>{message}</level>",
        },
        "message": {
            "sink": "apprise",
            "level": "SUCCESS",
            "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}:{function}:{line}</cyan> | "
            "<level>{message}</level>",
            "filter": {"apprise": False},
        },
    }
    logger.configure(handlers=list(handlers.values()))
