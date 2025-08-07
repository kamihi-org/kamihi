"""
PostgreSQL datasource module.

License:
    MIT
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from loguru import logger

from kamihi.base.utils import requires, timer

from .datasource import DataSource, DataSourceConfig

if TYPE_CHECKING:
    from loguru import Logger  # skipcq: TCV-001


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

    type: Literal["postgresql"] = "postgresql"

    host: str = "localhost"
    port: int = 5432
    database: str = "kamihi"
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

    type: Literal["postgresql"] = "postgresql"

    settings: PostgresDataSourceConfig

    _logger: Logger
    _pool: Any = None  # Placeholder for the connection pool type, typically asyncpg.Pool

    @cached_property
    @requires("postgresql")
    def NamedRecord(self) -> type:  # noqa: N802
        """Create a named record class for asyncpg records."""
        import asyncpg

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
                return self[name]  # skipcq: TCV-001

        return NamedRecord

    @requires("postgresql")
    def __init__(self, settings: PostgresDataSourceConfig) -> None:
        """
        Initialize the PostgresDataSource with the provided configuration.

        Args:
            settings (PostgresDataSourceConfig): The configuration for the PostgreSQL data source.

        """
        super().__init__(settings)
        self.settings = settings
        self._logger = logger.bind(datasource=settings.name, type=settings.type)

    async def connect(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ARG002
        """
        Initialize the connection pool for the PostgreSQL database.

        This method is called to set up the connection pool for the PostgreSQL database.
        It uses asyncpg to create a connection pool with the provided settings.

        Raises:
            RuntimeError: If asyncpg is not installed.
            ConnectionError: If the connection pool initialization fails.

        """
        import asyncpg

        if self._pool is not None:
            self._logger.warning("Connection pool already initialized, skipping re-initialization")
            return

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
            self._logger.info("Connected")
        except asyncpg.PostgresError as e:
            raise ConnectionError("Failed to initialize connection pool") from e

    async def fetch(self, request: Path | str) -> list[NamedRecord]:
        """
        Fetch data asynchronously from the PostgreSQL database.

        This method executes a SQL request from a file and returns the results.

        Args:
            request (Path | str): The path to the SQL request file or the SQL query as a string.

        Returns:
            list[NamedRecord]: The results obtained from the SQL request.

        """
        if not self._pool:
            raise RuntimeError("Connection pool is not initialized. Call connect() first.")

        with self._logger.contextualize(request=str(request)), timer(self._logger, "Executed command"):
            async with self._pool.acquire() as conn:
                self._logger.trace("Acquired connection from pool")
                results = await conn.fetch(request.read_text() if isinstance(request, Path) else request)
                self._logger.trace("Fetched {results} results from datasource", results=len(results))
        return results

    async def disconnect(self) -> None:
        """
        Disconnect from the PostgreSQL database asynchronously.

        This method closes the connection pool if it is initialized.

        """
        if self._pool is not None:
            self._logger.trace("Closing connection pool...")
            await self._pool.close()
            self._logger.info("Disconnected")
            self._pool = None
