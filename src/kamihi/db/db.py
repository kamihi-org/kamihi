"""
Database connection module for the Kamihi framework.

License:
    MIT

"""

import time

from loguru import logger
from sqlalchemy import Engine, create_engine, event

from kamihi.base import get_settings

_engine: Engine | None = None


def init_engine() -> None:
    """Initialize the database engine."""
    global _engine  # skipcq: PYL-W0603

    db_settings = get_settings().db

    if _engine is None:
        _engine = create_engine(db_settings.url)


def get_engine() -> Engine:
    """
    Create a database engine.

    Returns:
        Engine: The database engine.

    """
    if _engine is None:
        raise RuntimeError("Database engine is not initialized. Call init_engine() first.")
    return _engine


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _) -> None:  # noqa: ANN001
    """Set SQLite PRAGMA settings on connection."""
    from sqlite3 import Connection as SQLite3Connection

    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
        logger.debug("SQLite foreign key support enabled")


@event.listens_for(Engine, "before_cursor_execute")
def _before_cursor_execute(
    _conn,  # noqa: ANN001
    _cursor,  # noqa: ANN001
    _statement,  # noqa: ANN001
    _parameters,  # noqa: ANN001
    context,  # noqa: ANN001
    _executemany,  # noqa: ANN001
) -> None:
    """Event listener to save the start time of a query before execution."""
    context.query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(
    _conn,  # noqa: ANN001
    _cursor,  # noqa: ANN001
    statement,  # noqa: ANN001
    _parameters,  # noqa: ANN001
    context,  # noqa: ANN001
    _executemany,  # noqa: ANN001
) -> None:
    """Events after execution."""
    total = time.time() - context.query_start_time
    logger.bind(statement=statement, ms=round(total * 1000, 2)).trace("Executed statement")
