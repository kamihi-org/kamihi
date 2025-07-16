"""
Data sources module for Kamihi.

License:
    MIT
"""

from .datasource import DataSource, DataSourceConfig
from .postgres import PostgresDataSource, PostgresDataSourceConfig
from .sqlite import SQLiteDataSource, SQLiteDataSourceConfig

DataSourceConfigUnion = PostgresDataSourceConfig | SQLiteDataSourceConfig

__all__ = [
    "PostgresDataSource",
    "PostgresDataSourceConfig",
    "SQLiteDataSource",
    "SQLiteDataSourceConfig",
    "DataSourceConfig",
    "DataSourceConfigUnion",
]
