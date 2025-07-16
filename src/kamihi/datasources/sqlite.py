"""
SQLite datasource module.

License:
    MIT

"""

from pathlib import Path
from typing import Literal

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

    def __init__(self, settings: SQLiteDataSourceConfig) -> None:
        """
        Initialize the SQLiteDataSource with the provided configuration.

        Args:
            settings (SQLiteDataSourceConfig): The configuration for the SQLite data source.

        """
        super().__init__(settings)
        self.settings = settings
