"""
PostgreSQL datasource module.

License:
    MIT
"""

import time
from functools import cached_property
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, Never

import loguru
from loguru import logger

from .datasource import DataSource, DataSourceConfig


class PostgresDataSourceConfig(DataSourceConfig):
    """
    Configuration model for PostgreSQL data sources.

    This model extends the base DataSourceConfig to include specific parameters
    required for connecting to a PostgreSQL database.

    Attributes:
        host (str): The hostname of the PostgreSQL server.
        port (int): The port number of the PostgreSQL server.
        user (str): The username for connecting to the PostgreSQL database.
        password (str): The password for the specified user.
        database (str): The name of the PostgreSQL database to connect to.

    """

    type: Literal["postgresql"]

    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "postgres"
    password: str
    min_pool_size: int = 5
    max_pool_size: int = 10
    timeout: int = 60


class PostgresDataSource(DataSource):
    """
    PostgreSQL data source implementation.

    This class implements the DataSource interface for connecting to and interacting
    with a PostgreSQL database.
    """

    settings: PostgresDataSourceConfig

    _logger: loguru.Logger
    _pool: Any = None  # Placeholder for the connection pool type, typically asyncpg.Pool

    @cached_property
    def _asyncpg(self) -> ModuleType:
        """
        Import the asyncpg library for PostgreSQL database interaction.

        This method attempts to import the asyncpg library, which is required for
        asynchronous database operations. If the library is not installed, it raises
        a RuntimeError with instructions on how to install it.

        Raises:
            RuntimeError: If asyncpg is not installed.

        """
        try:
            import asyncpg
        except ImportError as e:
            raise RuntimeError(
                "To use the PostgreSQL data source, "
                "you must install kamihi with the 'postgres' extra: "
                "`uv add kamihi[postgres]`"
            ) from e

        return asyncpg

    @cached_property
    def NamedRecord(self) -> type:  # noqa: N802
        """Create a named record class for asyncpg records."""
        asyncpg = self._asyncpg

        class NamedRecord(asyncpg.Record):
            """
            A named record class that allows attribute access by name.

            This class extends asyncpg.Record to provide a way to access record fields
            using attribute-style access (e.g., record.field_name) instead of dictionary-style
            access (e.g., record['field_name']).
            """

            def __getattr__(self, name: str) -> Any:  # noqa: ANN401
                """
                Get an attribute by name.

                Args:
                    name (str): The name of the attribute to retrieve.

                Returns:
                    Any: The value of the attribute.

                """
                return self[name]

        return NamedRecord

    def __init__(self, settings: PostgresDataSourceConfig) -> None:
        """
        Initialize the PostgresDataSource with the provided configuration.

        Args:
            settings (PostgresDataSourceConfig): The configuration for the PostgreSQL data source.

        """
        super().__init__(settings)
        self.settings = settings
        self._logger = logger.bind(datasource=settings.name, type=settings.type)

    async def connect(self) -> None:
        """
        Initialize the connection pool for the PostgreSQL database.

        This method is not implemented for synchronous connections.

        Raises:
            NotImplementedError: This method is not implemented for synchronous connections.

        """
        raise NotImplementedError("Synchronous connection is not implemented. Use aconnect() instead")

    async def aconnect(self) -> None:
        """
        Initialize the connection pool for the PostgreSQL database.

        This method is called to set up the connection pool for the PostgreSQL database.
        It uses asyncpg to create a connection pool with the provided settings.

        Raises:
            RuntimeError: If asyncpg is not installed.
            ConnectionError: If the connection pool initialization fails.

        """
        if self._pool is not None:
            self._logger.warning("Connection pool already initialized, skipping re-initialization")
            return

        asyncpg = self._asyncpg

        try:
            self._pool = await asyncpg.create_pool(
                host=self.settings.host,
                port=self.settings.port,
                database=self.settings.database,
                user=self.settings.user,
                password=self.settings.password,
                min_size=self.settings.min_pool_size,
                max_size=self.settings.max_pool_size,
                timeout=self.settings.timeout,
                record_class=self.NamedRecord,
            )
            self._logger.debug("Connection pool initialized successfully")
        except asyncpg.PostgresError as e:
            raise ConnectionError("Failed to initialize connection pool") from e

    def fetch(self) -> Never:
        """
        Fetch data synchronously from the PostgreSQL database.

        This method will raise NotImplementedError as the only suppoerted method is async.

        Raises:
            NotImplementedError: This method is not implemented for synchronous fetching.

        """
        raise NotImplementedError("Synchronous fetch is not implemented. Use afetch() instead")

    async def afetch(self, request: Path) -> list[NamedRecord]:
        """
        Fetch data asynchronously from the PostgreSQL database.

        This method executes a SQL request from a file and returns the results.

        Args:
            request (Path): The path to the SQL request file.

        Returns:
            list[NamedRecord]: The results obtained from the SQL request.

        """
        if not self._pool:
            raise RuntimeError("Connection pool is not initialized. Call aconnect() first.")

        with self._logger.bind(request=str(request)) as log:
            async with self._pool.acquire() as conn:
                log.trace("Acquired connection from pool")
                start_time = time.perf_counter()
                results = await conn.fetch(request.read_text())
                end_time = time.perf_counter()
                log.debug(
                    "Executed command",
                    rows_returned=len(results),
                    elapsed_time=f"{(end_time - start_time) * 1000:.2f} ms",
                )
                return results

    def disconnect(self) -> None:
        """
        Disconnect from the PostgreSQL database.

        This method is not implemented for synchronous connections.

        Raises:
            NotImplementedError: This method is not implemented for synchronous connections.

        """
        raise NotImplementedError("Synchronous disconnect is not implemented. Use adisconnect() instead.")

    async def adisconnect(self) -> None:
        """
        Disconnect from the PostgreSQL database asynchronously.

        This method closes the connection pool if it is initialized.

        """
        if self._pool is not None:
            self._logger.trace("Closing connection pool...")
            await self._pool.close()
            self._logger.debug("Connection pool closed successfully.")
            self._pool = None
