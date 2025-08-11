"""
Tests for the SQLite DataSource class.

License:
    MIT
"""

import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path
from logot import Logot, logged

from kamihi.datasources.sqlite import SQLiteDataSourceConfig, SQLiteDataSource


@pytest.fixture
def sqlite_config():
    """Fixture to provide a SQLiteDataSourceConfig instance."""
    return SQLiteDataSourceConfig(name="test_db", path="/path/to/test.db")


@pytest.fixture
def mock_aiosqlite():
    """Fixture to mock the aiosqlite module and its connection behavior."""
    mock_aiosqlite_module = AsyncMock()
    mock_connection = AsyncMock()
    mock_cursor = AsyncMock()

    # Configure mocks
    mock_aiosqlite_module.connect = AsyncMock(return_value=mock_connection)
    mock_aiosqlite_module.Error = Exception

    # Set up the async context manager for execute
    # Use a Mock that can be asserted on while still returning the context manager
    from unittest.mock import Mock

    def mock_execute(query):
        return AsyncContextManager(mock_cursor)

    # Wrap the function in a Mock to enable assertions
    mock_connection.execute = Mock(side_effect=mock_execute)

    # Patch sys.modules to intercept all imports of aiosqlite
    with patch.dict("sys.modules", {"aiosqlite": mock_aiosqlite_module}):
        yield mock_aiosqlite_module, mock_connection, mock_cursor


class AsyncContextManager:
    """Helper class to create an async context manager for the cursor."""

    def __init__(self, cursor):
        """
        Initialize the async context manager with a cursor.

        Args:
            cursor: The cursor to be used in the context manager.

        """
        self.cursor = cursor

    async def __aenter__(self):
        """Enter the async context manager."""
        return self.cursor

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        return None


def test_sqlite_config_uses_default_type():
    """Test that SQLiteDataSourceConfig uses 'sqlite' as the default type."""
    config = SQLiteDataSourceConfig(name="test", path="/path/to/db.sqlite")
    assert config.type == "sqlite"


def test_sqlite_config_string_path():
    """Test that SQLiteDataSourceConfig accepts a string path."""
    config = SQLiteDataSourceConfig(name="test", path="/path/to/database.db")
    assert config.path == "/path/to/database.db"


def test_sqlite_config_pathlib_path():
    """Test that SQLiteDataSourceConfig accepts a pathlib.Path object."""
    path = Path("/path/to/database.db")
    config = SQLiteDataSourceConfig(name="test", path=path)
    assert config.path == path


@pytest.mark.asyncio
async def test_sqlite_source_connect(sqlite_config, mock_aiosqlite, logot: Logot):
    """Test connecting to the SQLite database."""
    mock_aiosqlite_module, mock_connection, _ = mock_aiosqlite

    datasource = SQLiteDataSource(sqlite_config)
    await datasource.connect()

    mock_aiosqlite_module.connect.assert_called_once_with(sqlite_config.path)
    assert datasource._db is mock_connection
    logot.assert_logged(logged.info("Connected"))


@pytest.mark.asyncio
async def test_sqlite_source_connect_already_connected(sqlite_config, mock_aiosqlite, logot: Logot):
    """Test connecting to the SQLite database when already connected."""
    mock_aiosqlite_module, _, _ = mock_aiosqlite

    datasource = SQLiteDataSource(sqlite_config)
    await datasource.connect()
    logot.assert_logged(logged.info("Connected"))

    # Attempt to connect again
    await datasource.connect()

    # Should only be called once, not twice
    assert mock_aiosqlite_module.connect.call_count == 1
    logot.assert_logged(logged.warning("Already connected, skipping re-initialization"))


@pytest.mark.asyncio
async def test_sqlite_source_connect_error(sqlite_config, mock_aiosqlite):
    """Test connecting to the SQLite database when an error occurs."""
    mock_aiosqlite_module, _, _ = mock_aiosqlite
    mock_aiosqlite_module.connect.side_effect = mock_aiosqlite_module.Error("Connection failed")

    datasource = SQLiteDataSource(sqlite_config)

    with pytest.raises(RuntimeError, match="Failed to connect"):
        await datasource.connect()


@pytest.mark.asyncio
async def test_sqlite_source_fetch_string(sqlite_config, mock_aiosqlite, logot: Logot):
    """Test fetching data from the SQLite database using a string query."""
    _, mock_connection, mock_cursor = mock_aiosqlite

    # Mock results
    mock_results = [{"id": 1, "name": "Test"}]
    mock_cursor.fetchall.return_value = mock_results

    datasource = SQLiteDataSource(sqlite_config)
    await datasource.connect()

    query = "SELECT * FROM test_table"
    results = await datasource.fetch(query)

    # Now we can assert on both the execute call and fetchall
    mock_connection.execute.assert_called_once_with(query)
    mock_cursor.fetchall.assert_called_once()
    assert results == mock_results
    logot.assert_logged(logged.debug("Executed command"))


@pytest.mark.asyncio
async def test_sqlite_source_fetch_file(sqlite_config, mock_aiosqlite, tmp_path, logot: Logot):
    """Test fetching data from the SQLite database using a SQL file."""
    _, mock_connection, mock_cursor = mock_aiosqlite

    # Create a temporary SQL file
    sql_file = tmp_path / "query.sql"
    sql_content = "SELECT * FROM users WHERE active = 1"
    sql_file.write_text(sql_content)

    mock_results = [{"id": 1, "name": "Active User"}]
    mock_cursor.fetchall.return_value = mock_results

    datasource = SQLiteDataSource(sqlite_config)
    await datasource.connect()

    results = await datasource.fetch(sql_file)

    mock_connection.execute.assert_called_once_with(sql_content)
    mock_cursor.fetchall.assert_called_once()
    assert results == mock_results
    logot.assert_logged(logged.debug("Executed command"))


@pytest.mark.asyncio
async def test_sqlite_source_fetch_disconnected(sqlite_config):
    """Test fetching data from the SQLite database when not connected."""
    datasource = SQLiteDataSource(sqlite_config)

    with pytest.raises(RuntimeError, match="Database connection is not established. Call connect\\(\\) first."):
        await datasource.fetch("SELECT * FROM test_table")


@pytest.mark.asyncio
async def test_sqlite_source_disconnect(sqlite_config, mock_aiosqlite, logot: Logot):
    """Test disconnecting from the SQLite database."""
    _, mock_connection, _ = mock_aiosqlite

    datasource = SQLiteDataSource(sqlite_config)
    await datasource.connect()
    await datasource.disconnect()

    mock_connection.close.assert_called_once()
    assert datasource._db is None
    logot.assert_logged(logged.info("Disconnected"))


@pytest.mark.asyncio
async def test_sqlite_source_disconnect_already_disconnected(sqlite_config, mock_aiosqlite, logot: Logot):
    """Test disconnecting from the SQLite database when already disconnected."""
    _, mock_connection, _ = mock_aiosqlite

    datasource = SQLiteDataSource(sqlite_config)
    await datasource.connect()
    await datasource.disconnect()
    logot.assert_logged(logged.info("Disconnected"))

    # Disconnect again
    await datasource.disconnect()

    # Should only close once
    assert mock_connection.close.call_count == 1
