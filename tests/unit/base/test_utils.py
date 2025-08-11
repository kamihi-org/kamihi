"""
Tests for the kamihi.base.utils module.

License:
    MIT

"""

import importlib.metadata
import time
from unittest.mock import Mock

import pytest
from logot import Logot, logged
from loguru import logger

from kamihi.base.utils import requires, _check_extra_installed, timer


def test_requires_decorator_success(monkeypatch):
    """Test requires decorator when all dependencies are installed."""
    # Mock successful dependency checks
    mock_requires = ["test-package>=1.0; extra == 'test'", "another-package; extra == 'test'"]
    mock_metadata_requires = Mock(return_value=mock_requires)
    mock_distribution = Mock()

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)
    monkeypatch.setattr("importlib.metadata.distribution", mock_distribution)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function(x, y):
        return x + y

    # Function should execute normally
    result = test_function(1, 2)
    assert result == 3

    # Verify metadata calls
    mock_metadata_requires.assert_called_once_with("kamihi")
    assert mock_distribution.call_count == 2  # Called for each dependency


def test_requires_decorator_missing_dependency(monkeypatch):
    """Test requires decorator when a dependency is missing."""
    # Mock requirements with one missing dependency
    mock_requires = ["test-package>=1.0; extra == 'test'", "missing-package; extra == 'test'"]
    mock_metadata_requires = Mock(return_value=mock_requires)

    def mock_distribution(pkg):
        if pkg == "missing-package":
            raise importlib.metadata.PackageNotFoundError()
        return Mock()

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)
    monkeypatch.setattr("importlib.metadata.distribution", mock_distribution)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function(x, y):
        return x + y

    # Function should raise ImportError
    with pytest.raises(ImportError, match=r"Missing required optional dependency 'missing-package' for group 'test'"):
        test_function(1, 2)


def test_requires_decorator_no_package_metadata(monkeypatch):
    """Test requires decorator when package metadata is not found."""
    # Mock PackageNotFoundError for the main package
    mock_metadata_requires = Mock(side_effect=importlib.metadata.PackageNotFoundError())

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function(x, y):
        return x + y

    # Function should execute normally when no metadata is found (empty requirements)
    result = test_function(1, 2)
    assert result == 3


def test_requires_decorator_no_matching_extra(monkeypatch):
    """Test requires decorator when no dependencies match the extra group."""
    # Mock requirements with no matching extra
    mock_requires = ["some-package>=1.0; extra == 'other'", "another-package; extra == 'different'"]
    mock_metadata_requires = Mock(return_value=mock_requires)

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function(x, y):
        return x + y

    # Function should execute normally when no dependencies for the group
    result = test_function(1, 2)
    assert result == 3


def test_requires_decorator_complex_dependency_parsing(monkeypatch):
    """Test requires decorator with complex dependency specifications."""
    # Mock requirements with complex version specifications
    mock_requires = [
        "test-package[extra]>=1.0,<2.0; extra == 'test'",
        "another-package==1.2.3; extra == 'test'",
        "third-package; extra == 'test'",
    ]
    mock_metadata_requires = Mock(return_value=mock_requires)
    mock_distribution = Mock()

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)
    monkeypatch.setattr("importlib.metadata.distribution", mock_distribution)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function():
        return "success"

    # Function should execute normally
    result = test_function()
    assert result == "success"

    # Verify correct package names were extracted and checked
    expected_calls = ["test-package", "another-package", "third-package"]
    actual_calls = [call[0][0] for call in mock_distribution.call_args_list]
    assert actual_calls == expected_calls


def test_requires_decorator_preserves_function_metadata(monkeypatch):
    """Test that the requires decorator preserves function metadata."""
    # Mock successful dependency checks
    mock_requires = []
    mock_metadata_requires = Mock(return_value=mock_requires)

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function(x: int, y: int) -> int:
        """Test function docstring."""
        return x + y

    # Verify function metadata is preserved
    assert test_function.__name__ == "test_function"
    assert test_function.__doc__ == "Test function docstring."
    assert hasattr(test_function, "__wrapped__")


def test_requires_decorator_with_async_function(monkeypatch):
    """Test requires decorator with async functions."""
    # Mock successful dependency checks
    mock_requires = []
    mock_metadata_requires = Mock(return_value=mock_requires)

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    async def async_test_function(x, y):
        return x + y

    # Verify the decorator works with async functions
    import asyncio

    result = asyncio.run(async_test_function(1, 2))
    assert result == 3


def test_requires_decorator_caching(monkeypatch):
    """Test that _check_extra_installed uses caching properly."""
    # Mock successful dependency checks
    mock_requires = ["test-package; extra == 'test'"]
    mock_metadata_requires = Mock(return_value=mock_requires)
    mock_distribution = Mock()

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)
    monkeypatch.setattr("importlib.metadata.distribution", mock_distribution)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function():
        return "success"

    # Call the function multiple times
    test_function()
    test_function()
    test_function()

    # Verify metadata.requires is only called once due to caching
    mock_metadata_requires.assert_called_once_with("kamihi")
    mock_distribution.assert_called_once_with("test-package")


def test_requires_decorator_with_kwargs_and_args(monkeypatch):
    """Test requires decorator with functions that use *args and **kwargs."""
    # Mock successful dependency checks
    mock_requires = []
    mock_metadata_requires = Mock(return_value=mock_requires)

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("test")
    def test_function(*args, **kwargs):
        return sum(args) + sum(kwargs.values())

    # Function should work with various argument patterns
    result1 = test_function(1, 2, 3)
    assert result1 == 6

    result2 = test_function(a=1, b=2, c=3)
    assert result2 == 6

    result3 = test_function(1, 2, c=3, d=4)
    assert result3 == 10


def test_check_extra_installed_error_message_format(monkeypatch):
    """Test the error message format when dependencies are missing."""
    # Mock requirements with missing dependency
    mock_requires = ["missing-package>=1.0; extra == 'mygroup'"]
    mock_metadata_requires = Mock(return_value=mock_requires)

    def mock_distribution(pkg):
        raise importlib.metadata.PackageNotFoundError()

    monkeypatch.setattr("importlib.metadata.requires", mock_metadata_requires)
    monkeypatch.setattr("importlib.metadata.distribution", mock_distribution)

    # Clear the cache for _check_extra_installed
    _check_extra_installed.cache_clear()

    @requires("mygroup")
    def test_function():
        return "success"

    # Verify the exact error message format
    with pytest.raises(ImportError) as exc_info:
        test_function()

    error_msg = str(exc_info.value)
    assert "Missing required optional dependency 'missing-package' for group 'mygroup'" in error_msg
    assert "Please run 'uv add kamihi[mygroup]' to install." in error_msg


def test_timer_context_manager(logot: Logot):
    """Test timer context manager with default DEBUG level."""
    message = "Test operation completed"
    with timer(logger, message):
        time.sleep(0.01)  # Small delay to ensure measurable time

    # Verify the message was logged
    logot.assert_logged(logged.debug(message))


def test_timer_custom_log_level(logot: Logot):
    """Test timer context manager with custom log level."""
    message = "Custom level operation"
    level = "INFO"

    with timer(logger, message, level):
        time.sleep(0.01)  # Small delay to ensure measurable time

    # Verify the message was logged
    logot.assert_logged(logged.log(level, message))


def test_timer_timing_accuracy(logot: Logot):
    """Test that timer measures time accurately."""
    mock_logger = Mock()
    mock_bind = Mock()
    mock_logger.bind.return_value = mock_bind

    sleep_duration = 0.05  # 50ms

    with timer(mock_logger, "Timing test"):
        time.sleep(sleep_duration)

    # Verify the timing is reasonable (should be around 50ms, allowing for some variance)
    call_args = mock_logger.bind.call_args[1]
    measured_ms = call_args["ms"]

    # Should be close to 50ms, but allow variance for system timing
    assert 40 <= measured_ms <= 100
