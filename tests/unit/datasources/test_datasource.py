"""
Tests for the base DataSource class and associated DataSourceConfig class.

License:
    MIT

"""

from types import NoneType
from typing import Union, get_origin, Annotated
from unittest.mock import AsyncMock

import pytest

from kamihi.datasources import DataSource, DataSourceConfig


# skipcq: PYL-W0223
class MockDataSourceConfig(DataSourceConfig):
    """Mock DataSourceConfig for testing."""

    type: str = "mock"


# skipcq: PYL-W0223
class MockDataSource(DataSource):
    """Mock DataSource for testing."""

    type = "mock"


# skipcq: PYL-W0223
class AnotherMockDataSourceConfig(DataSourceConfig):
    """Another mock DataSourceConfig for testing."""

    type: str = "another_mock"


# skipcq: PYL-W0223
class AnotherMockDataSource(DataSource):
    """Another mock DataSource for testing."""

    type = "another_mock"


def test_config_init():
    """DataSourceConfig initializes with name."""
    config = DataSourceConfig(name="test_datasource")

    assert config.name == "test_datasource"


def test_config_build_registry():
    """DataSourceConfig builds registry from subclasses."""
    DataSourceConfig._registry = {}

    DataSourceConfig._build_registry()

    assert "mock" in DataSourceConfig._registry
    assert DataSourceConfig._registry["mock"] == MockDataSourceConfig


def test_config_union_type():
    """DataSourceConfig returns union type of all registered classes."""
    DataSourceConfig._registry = {"mock": MockDataSourceConfig, "another_mock": AnotherMockDataSourceConfig}

    result = DataSourceConfig.union_type()

    assert get_origin(result) is Annotated

    union_type = result.__args__[0]
    assert get_origin(union_type) is Union
    assert union_type.__args__ == (MockDataSourceConfig, AnotherMockDataSourceConfig)


def test_config_union_type_no_registry(monkeypatch):
    """DataSourceConfig builds registry when empty before returning union type."""
    DataSourceConfig._registry = {}

    result = DataSourceConfig.union_type()

    assert get_origin(result) is Annotated

    union_type = result.__args__[0]
    assert get_origin(union_type) is Union
    assert MockDataSourceConfig in union_type.__args__
    assert AnotherMockDataSourceConfig in union_type.__args__


def test_config_union_type_empty(monkeypatch):
    """DataSourceConfig returns DataSourceConfig when no subclasses exist."""
    DataSourceConfig._registry = {}
    monkeypatch.setattr(DataSourceConfig, "_build_registry", AsyncMock())

    result = DataSourceConfig.union_type()

    assert result == NoneType


def test_datasource_init():
    """DataSource initializes and stores settings."""
    config = DataSourceConfig(name="test_datasource")
    datasource = DataSource(config)

    assert datasource.settings == config
    assert datasource.settings.name == "test_datasource"


def test_datasource_build_registry():
    """DataSource builds registry from subclasses."""
    DataSource._registry = {}

    DataSource._build_registry()

    assert "mock" in DataSource._registry
    assert DataSource._registry["mock"] == MockDataSource


def test_datasource_get_datasource_class():
    """DataSource returns existing class from registry."""
    DataSource._registry = {"mock": MockDataSource}

    result = DataSource.get_datasource_class("mock")

    assert result == MockDataSource


def test_datasource_get_datasource_class_no_registry():
    """DataSource builds registry when empty before returning class."""
    DataSource._registry = {}

    result = DataSource.get_datasource_class("mock")

    assert result == MockDataSource
    assert "mock" in DataSource._registry


def test_datasource_get_datasource_class_unknown():
    """DataSource returns None for unknown type."""
    DataSource._registry = {"mock": MockDataSource}

    result = DataSource.get_datasource_class("unknown")

    assert result is None


@pytest.mark.asyncio
async def test_datasource_connect():
    """DataSource connect method does nothing by default."""
    config = DataSourceConfig(name="test")
    datasource = DataSource(config)

    with pytest.raises(NotImplementedError, match="Subclasses must implement this method"):
        await datasource.connect()


@pytest.mark.asyncio
async def test_datasource_fetch():
    """DataSource fetch method raises NotImplementedError."""
    config = DataSourceConfig(name="test")
    datasource = DataSource(config)

    with pytest.raises(NotImplementedError, match="Subclasses must implement this method"):
        await datasource.fetch("SELECT * FROM test_table")


@pytest.mark.asyncio
async def test_datasource_disconnect():
    """DataSource disconnect method does nothing by default."""
    config = DataSourceConfig(name="test")
    datasource = DataSource(config)

    with pytest.raises(NotImplementedError, match="Subclasses must implement this method"):
        await datasource.disconnect()
