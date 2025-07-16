"""
PostgreSQL datasource module.

License:
    MIT
"""

from typing import Literal

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

    host: str
    port: int
    user: str
    password: str
    database: str


class PostgresDataSource(DataSource):
    """
    PostgreSQL data source implementation.

    This class implements the DataSource interface for connecting to and interacting
    with a PostgreSQL database.
    """

    def __init__(self, settings: PostgresDataSourceConfig) -> None:
        """
        Initialize the PostgresDataSource with the provided configuration.

        Args:
            settings (PostgresDataSourceConfig): The configuration for the PostgreSQL data source.

        """
        super().__init__(settings)
        self.settings = settings
