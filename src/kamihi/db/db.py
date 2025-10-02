"""
Database connection module for the Kamihi framework.

License:
    MIT

"""

import time

from loguru import logger
from sqlalchemy import Engine, create_engine, event

from kamihi.base.config import DatabaseSettings

_engine: Engine | None = None


def init_engine(db_settings: DatabaseSettings) -> None:
    """
    Initialize the database engine.

    Args:
        db_settings (DatabaseSettings): The database settings.

    """
    global _engine
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
    conn,  # noqa: ANN001, ARG001
    cursor,  # noqa: ANN001, ARG001
    statement,  # noqa: ANN001, ARG001
    parameters,  # noqa: ANN001, ARG001
    context,  # noqa: ANN001
    executemany,  # noqa: ANN001, ARG001
) -> None:
    """Event listener to save the start time of a query before execution."""
    context.query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(
    conn,  # noqa: ANN001, ARG001
    cursor,  # noqa: ANN001, ARG001
    statement,  # noqa: ANN001, ARG001
    parameters,  # noqa: ANN001, ARG001
    context,  # noqa: ANN001
    executemany,  # noqa: ANN001, ARG001
) -> None:
    """Events after execution."""
    total = time.time() - context.query_start_time
    logger.bind(statement=statement, ms=round(total * 1000, 2)).trace("Executed statement")
