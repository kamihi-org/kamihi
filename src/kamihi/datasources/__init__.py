"""
Data sources module for Kamihi.

License:
    MIT
"""

from .datasource import DataSource, DataSourceConfig
from .postgres import PostgresDataSource, PostgresDataSourceConfig
from .sqlite import SQLiteDataSource, SQLiteDataSourceConfig

__all__ = [
    "DataSource",
    "DataSourceConfig",
    "PostgresDataSource",
    "PostgresDataSourceConfig",
    "SQLiteDataSource",
    "SQLiteDataSourceConfig",
]
