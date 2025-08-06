"""
Tests for the Postgres DataSource class.

License:
    MIT
"""

import pytest
from unittest.mock import patch, AsyncMock
from logot import Logot, logged

from kamihi.datasources.postgres import PostgresDataSourceConfig, PostgresDataSource


@pytest.fixture
def postgres_config():
    return PostgresDataSourceConfig(
        name="test_db", host="test.host", database="test_db", user="test_user", password="test_password"
    )


@pytest.fixture
def mock_asyncpg():
    # Create the mock module
    import asyncpg

    mock_asyncpg_module = AsyncMock(spec=asyncpg)
    mock_pool = AsyncMock(spec=asyncpg.Pool)
    mock_conn = AsyncMock(spec=asyncpg.Connection)

    # Configure mocks
    mock_pool.acquire.return_value = AsyncMock(spec=asyncpg.pool.PoolAcquireContext)
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_asyncpg_module.create_pool = AsyncMock(spec=asyncpg.create_pool, return_value=mock_pool)
    mock_asyncpg_module.Record = type("Record", (), {})
    mock_asyncpg_module.PostgresError = Exception

    # Patch sys.modules to intercept all imports of asyncpg
    with patch.dict("sys.modules", {"asyncpg": mock_asyncpg_module}):
        yield mock_asyncpg_module, mock_pool, mock_conn


def test_postgres_config_defaults():
    config = PostgresDataSourceConfig(name="test", password="password123")
    assert config.type == "postgresql"
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.database == "kamihi"
    assert config.user == "postgres"
    assert config.password == "password123"
    assert config.min_pool_size == 5
    assert config.max_pool_size == 10
    assert config.timeout == 60


def test_postgres_config_custom():
    config = PostgresDataSourceConfig(
        name="custom_db",
        host="db.example.com",
        port=5433,
        database="app_db",
        user="app_user",
        password="secure_pass",
        min_pool_size=2,
        max_pool_size=20,
        timeout=30,
    )
    assert config.host == "db.example.com"
    assert config.port == 5433
    assert config.database == "app_db"
    assert config.name == "custom_db"


@pytest.mark.asyncio
async def test_postgres_source_connect(postgres_config, mock_asyncpg, logot: Logot):
    mock_asyncpg_module, _, _ = mock_asyncpg

    datasource = PostgresDataSource(postgres_config)
    await datasource.connect()

    # Verify connection parameters
    mock_asyncpg_module.create_pool.assert_called_once()
    call_kwargs = mock_asyncpg_module.create_pool.call_args.kwargs
    assert call_kwargs["host"] == postgres_config.host
    assert call_kwargs["user"] == postgres_config.user

    logot.assert_logged(logged.info("Connected"))


@pytest.mark.asyncio
async def test_postgres_source_connect_already_connected(postgres_config, mock_asyncpg, logot: Logot):
    mock_asyncpg_module, mock_pool, _ = mock_asyncpg
    datasource = PostgresDataSource(postgres_config)
    await datasource.connect()

    logot.assert_logged(logged.info("Connected"))

    # Test connecting when already connected
    await datasource.connect()  # Should log warning and skip
    assert mock_asyncpg_module.create_pool.call_count == 1
    logot.assert_logged(logged.warning("Connection pool already initialized, skipping re-initialization"))


@pytest.mark.asyncio
async def test_postgres_source_connect_error(postgres_config, mock_asyncpg):
    mock_asyncpg_module, _, _ = mock_asyncpg
    mock_asyncpg_module.create_pool.side_effect = mock_asyncpg_module.PostgresError("Connection failed")

    datasource = PostgresDataSource(postgres_config)
    with pytest.raises(ConnectionError):
        await datasource.connect()


@pytest.mark.asyncio
async def test_postgres_source_fetch_string(postgres_config, mock_asyncpg, logot: Logot):
    _, _, mock_conn = mock_asyncpg

    # Mock results
    mock_results = [{"id": 1, "name": "Test"}]
    mock_conn.fetch.return_value = mock_results

    datasource = PostgresDataSource(postgres_config)
    await datasource.connect()
    logot.assert_logged(logged.info("Connected"))

    # Test fetching with string query
    query = "SELECT * FROM test_table"
    results = await datasource.fetch(query)

    mock_conn.fetch.assert_called_once_with(query)
    assert results == mock_results

    logot.assert_logged(logged.debug("Executed command"))


@pytest.mark.asyncio
async def test_postgres_source_fetch_file(postgres_config, mock_asyncpg, tmp_path, logot: Logot):
    _, _, mock_conn = mock_asyncpg

    # Create a temporary SQL file
    sql_file = tmp_path / "query.sql"
    sql_content = "SELECT * FROM test_table"
    sql_file.write_text(sql_content)

    mock_results = [{"id": 1, "name": "Test"}]
    mock_conn.fetch.return_value = mock_results

    datasource = PostgresDataSource(postgres_config)
    await datasource.connect()
    logot.assert_logged(logged.info("Connected"))

    results = await datasource.fetch(sql_file)

    mock_conn.fetch.assert_called_once_with(sql_content)
    assert results == mock_results

    logot.assert_logged(logged.debug("Executed command"))


@pytest.mark.asyncio
async def test_postgres_source_fetch_disconnected(postgres_config):
    datasource = PostgresDataSource(postgres_config)

    with pytest.raises(RuntimeError, match="Connection pool is not initialized"):
        await datasource.fetch("SELECT * FROM test_table")


@pytest.mark.asyncio
async def test_postgres_source_disconnect(postgres_config, mock_asyncpg, logot: Logot):
    _, mock_pool, _ = mock_asyncpg

    datasource = PostgresDataSource(postgres_config)
    await datasource.connect()
    await datasource.disconnect()

    mock_pool.close.assert_called_once()
    assert datasource._pool is None
    logot.assert_logged(logged.info("Disconnected"))


@pytest.mark.asyncio
async def test_postgres_source_disconnect_already_disconnected(postgres_config, mock_asyncpg, logot: Logot):
    _, mock_pool, _ = mock_asyncpg

    datasource = PostgresDataSource(postgres_config)
    await datasource.connect()
    await datasource.disconnect()
    logot.assert_logged(logged.info("Disconnected"))

    # Test disconnecting when already disconnected
    await datasource.disconnect()  # Should not say anything or raise an error
