"""
SQLite datasource module.

License:
    MIT

"""

import time
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path
from sqlite3 import Row
from types import ModuleType
from typing import Any, Literal

from loguru import logger

from .datasource import DataSource, DataSourceConfig


class SQLiteDataSourceConfig(DataSourceConfig):
    """
    Configuration model for SQLite data sources.

    This model extends the base DataSourceConfig to include specific parameters
    required for connecting to an SQLite database.

    Attributes:
        type (Literal["sqlite"]): The type of the data source, which is "sqlite".
        path (str | Path): The path to the SQLite database file.

    """

    type: Literal["sqlite"] = "sqlite"

    path: str | Path


class SQLiteDataSource(DataSource):
    """
    SQLite data source implementation.

    This class implements the DataSource interface for connecting to and interacting
    with an SQLite database.

    Attributes:
        type (Literal["sqlite"]): The type of the data source, which is "sqlite".
        settings (SQLiteDataSourceConfig): The configuration for the SQLite data source.

    """

    type: Literal["sqlite"] = "sqlite"

    _db: Any = None  # Placeholder for the database connection

    @cached_property
    def _aiosqlite(self) -> ModuleType:
        """
        Lazy load the aiosqlite module.

        This method is used to import the aiosqlite module only when it is needed,
        which can help reduce startup time and memory usage if the module is not used.

        Returns:
            ModuleType: The aiosqlite module.

        """
        try:
            import aiosqlite
        except ImportError as e:
            raise RuntimeError(
                "To use the SQLite data source, "
                "you must install kamihi with the 'sqlite' extra: "
                "`uv add kamihi[sqlite]`"
            ) from e

        return aiosqlite

    def __init__(self, settings: SQLiteDataSourceConfig) -> None:
        """
        Initialize the SQLiteDataSource with the provided configuration.

        Args:
            settings (SQLiteDataSourceConfig): The configuration for the SQLite data source.

        """
        super().__init__(settings)
        self.settings = settings
        self._logger = logger.bind(datasource=settings.name, type=settings.type)

    async def connect(self) -> None:
        """
        Connect to the SQLite database.

        This method establishes a connection to the SQLite database specified in the
        settings. It uses the aiosqlite library for asynchronous database operations.

        """
        if self._db is not None:
            self._logger.warning("Already connected, skipping re-initialization")
            return

        try:
            self._db = await self._aiosqlite.connect(self.settings.path)
            self._logger.info("Connected")
        except self._aiosqlite.Error as e:
            raise RuntimeError("Failed to connect") from e

    async def fetch(self, request: Path | str) -> Iterable[Row]:
        """
        Fetch data from the SQLite database.

        This method executes a query against the SQLite database and returns the results.

        Args:
            request (Path | str): The SQL query to execute. This can be a path to a SQL file
                                  or a raw SQL string.

        Returns:
            Any: The results of the query.

        """
        if not self._db:
            raise RuntimeError("Database connection is not established. Call connect() first.")

        with self._logger.contextualize(request=str(request)):
            start_time = time.perf_counter()
            async with self._db.execute(request if isinstance(request, str) else request.read_text()) as cursor:
                results = await cursor.fetchall()
            end_time = time.perf_counter()
            self._logger.debug(
                "Executed command",
                rows_returned=len(results),
                ms=round((end_time - start_time) * 1000),
            )
            return results

    async def disconnect(self) -> None:
        """
        Disconnect from the SQLite database.

        This method closes the connection to the SQLite database.

        """
        if self._db:
            self._logger.trace("Closing database connection...")
            await self._db.close()
            self._logger.info("Disconnected")
            self._db = None
